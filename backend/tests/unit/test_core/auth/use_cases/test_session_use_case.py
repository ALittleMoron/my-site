# ruff: noqa: S106
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from core.auth.enums import RoleEnum
from core.auth.event_dispatchers import AuthEventReporter
from core.auth.exceptions import ForbiddenError, UnauthorizedError
from core.auth.generators import AuthSessionSecretGenerator
from core.auth.schemas import (
    AccessTokenPayload,
    AccessTokenResult,
    AuthAuthenticateParams,
    AuthLoginParams,
    AuthLoginResult,
    AuthLogoutParams,
    AuthRefreshAccessTokenParams,
    AuthSession,
    AuthSessionCreate,
    AuthSessionCredentials,
    AuthUseCaseConfig,
)
from core.auth.storages import AuthSessionStorage, AuthStorage, TokenRevocationStorage
from core.auth.types import SessionSecret, SessionSecretHash, Token
from core.auth.use_cases import AuthUseCase
from tests.test_cases import TestCase


class TestAuthSessionUseCase(TestCase):
    def setup_method(self) -> None:
        self.now = datetime(2026, 7, 8, 11, 30, tzinfo=UTC)
        self.hasher = Mock()
        self.token_handler = Mock()
        self.auth_storage = Mock(spec=AuthStorage)
        self.token_revocation_storage = Mock(spec=TokenRevocationStorage)
        self.token_revocation_storage.is_token_revoked.return_value = False
        self.session_storage = Mock(spec=AuthSessionStorage)
        self.user_storage = AsyncMock()
        self.event_reporter = Mock(spec=AuthEventReporter)
        self.session_secret_generator = Mock(spec=AuthSessionSecretGenerator)
        self.session_secret_generator.generate_secret.return_value = SessionSecret(
            "session-secret",
        )
        self.session_secret_generator.hash_secret.return_value = SessionSecretHash(
            "session-secret-hash",
        )
        self.session_storage.create_session.return_value = AuthSession(
            id="10000000000040008000000000000001",
            username="admin",
            secret_hash=SessionSecretHash("session-secret-hash"),
            expires_at=self.now + timedelta(seconds=2_592_000),
            is_revoked=False,
        )
        self.use_case = AuthUseCase(
            hasher=self.hasher,
            token_handler=self.token_handler,
            auth_storage=self.auth_storage,
            token_revocation_storage=self.token_revocation_storage,
            auth_session_storage=self.session_storage,
            user_storage=self.user_storage,
            event_reporter=self.event_reporter,
            auth_session_secret_generator=self.session_secret_generator,
            config=AuthUseCaseConfig(
                access_token_expires_in_seconds=900,
                session_expires_in_seconds=2_592_000,
            ),
        )

    async def test_login_creates_session_and_short_lived_access_token(self) -> None:
        self.hasher.verify_password.return_value = (True, False)
        self.token_handler.encode_token.return_value = Token(b"ACCESS")
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="admin",
            password_hash="hash",
            role=RoleEnum.ADMIN,
        )

        result = await self.use_case.login(
            params=AuthLoginParams(
                username="admin",
                password="password",
                required_role=RoleEnum.MODERATOR,
                current_datetime=self.now,
            ),
        )

        assert result == AuthLoginResult(
            access_token=AccessTokenResult(
                token=Token(b"ACCESS"),
                expires_in_seconds=900,
            ),
            session=AuthSessionCredentials(
                secret=SessionSecret("session-secret"),
                expires_in_seconds=2_592_000,
            ),
        )
        self.session_storage.create_session.assert_called_once_with(
            session=AuthSessionCreate(
                username="admin",
                secret_hash=SessionSecretHash("session-secret-hash"),
                expires_at=self.now + timedelta(seconds=2_592_000),
                is_revoked=False,
            ),
        )
        self.token_handler.encode_token.assert_called_once_with(
            payload=AccessTokenPayload(
                username="admin",
                session_id="10000000000040008000000000000001",
            ),
        )

    async def test_refresh_rejects_expired_session(self) -> None:
        self.session_storage.get_session_by_secret_hash.return_value = AuthSession(
            id="10000000000040008000000000000001",
            username="admin",
            secret_hash=SessionSecretHash("session-secret-hash"),
            expires_at=self.now - timedelta(seconds=1),
            is_revoked=False,
        )

        with pytest.raises(UnauthorizedError):
            await self.use_case.refresh_access_token(
                params=AuthRefreshAccessTokenParams(
                    session_secret=SessionSecret("session-secret"),
                    required_role=RoleEnum.MODERATOR,
                    current_datetime=self.now,
                ),
            )

        self.token_handler.encode_token.assert_not_called()

    async def test_refresh_rejects_revoked_session(self) -> None:
        self.session_storage.get_session_by_secret_hash.return_value = AuthSession(
            id="10000000000040008000000000000001",
            username="admin",
            secret_hash=SessionSecretHash("session-secret-hash"),
            expires_at=self.now + timedelta(days=1),
            is_revoked=True,
        )

        with pytest.raises(UnauthorizedError):
            await self.use_case.refresh_access_token(
                params=AuthRefreshAccessTokenParams(
                    session_secret=SessionSecret("session-secret"),
                    required_role=RoleEnum.MODERATOR,
                    current_datetime=self.now,
                ),
            )

        self.token_handler.encode_token.assert_not_called()

    async def test_refresh_rejects_session_user_without_required_role(self) -> None:
        self.session_storage.get_session_by_secret_hash.return_value = AuthSession(
            id="10000000000040008000000000000001",
            username="regular",
            secret_hash=SessionSecretHash("session-secret-hash"),
            expires_at=self.now + timedelta(days=1),
            is_revoked=False,
        )
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="regular",
            password_hash="hash",
            role=RoleEnum.USER,
        )

        with pytest.raises(ForbiddenError):
            await self.use_case.refresh_access_token(
                params=AuthRefreshAccessTokenParams(
                    session_secret=SessionSecret("session-secret"),
                    required_role=RoleEnum.MODERATOR,
                    current_datetime=self.now,
                ),
            )

    async def test_refresh_returns_new_access_token_for_active_session(self) -> None:
        self.session_storage.get_session_by_secret_hash.return_value = AuthSession(
            id="10000000000040008000000000000001",
            username="moderator",
            secret_hash=SessionSecretHash("session-secret-hash"),
            expires_at=self.now + timedelta(days=1),
            is_revoked=False,
        )
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="moderator",
            password_hash="hash",
            role=RoleEnum.MODERATOR,
        )
        self.token_handler.encode_token.return_value = Token(b"NEW_ACCESS")

        result = await self.use_case.refresh_access_token(
            params=AuthRefreshAccessTokenParams(
                session_secret=SessionSecret("session-secret"),
                required_role=RoleEnum.MODERATOR,
                current_datetime=self.now,
            ),
        )

        assert result == AccessTokenResult(token=Token(b"NEW_ACCESS"), expires_in_seconds=900)
        self.session_secret_generator.hash_secret.assert_called_once_with(
            secret=SessionSecret("session-secret"),
        )
        self.token_handler.encode_token.assert_called_once_with(
            payload=AccessTokenPayload(
                username="moderator",
                session_id="10000000000040008000000000000001",
            ),
        )

    async def test_authenticate_rejects_token_when_session_is_not_active(self) -> None:
        token = Token(b"ACCESS")
        self.token_handler.decode_token.return_value = AccessTokenPayload(
            username="admin",
            session_id="10000000000040008000000000000001",
        )
        self.session_storage.get_session_by_id.return_value = AuthSession(
            id="10000000000040008000000000000001",
            username="admin",
            secret_hash=SessionSecretHash("session-secret-hash"),
            expires_at=self.now + timedelta(days=1),
            is_revoked=True,
        )

        with pytest.raises(UnauthorizedError):
            await self.use_case.authenticate(
                params=AuthAuthenticateParams(
                    token=token,
                    required_role=RoleEnum.MODERATOR,
                    current_datetime=self.now,
                ),
            )

        self.user_storage.get_user_by_username.assert_not_called()

    async def test_authenticate_loads_current_user_after_access_token_and_session_pass(
        self,
    ) -> None:
        token = Token(b"ACCESS")
        self.token_handler.decode_token.return_value = AccessTokenPayload(
            username="admin",
            session_id="10000000000040008000000000000001",
        )
        self.session_storage.get_session_by_id.return_value = AuthSession(
            id="10000000000040008000000000000001",
            username="admin",
            secret_hash=SessionSecretHash("session-secret-hash"),
            expires_at=self.now + timedelta(days=1),
            is_revoked=False,
        )
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="admin",
            password_hash="hash",
            role=RoleEnum.ADMIN,
        )

        user = await self.use_case.authenticate(
            params=AuthAuthenticateParams(
                token=token,
                required_role=RoleEnum.MODERATOR,
                current_datetime=self.now,
            ),
        )

        assert user == self.factory.core.user(
            username="admin",
            password_hash="hash",
            role=RoleEnum.ADMIN,
        )
        self.session_storage.get_session_by_id.assert_called_once_with(
            session_id="10000000000040008000000000000001",
        )

    async def test_logout_revokes_session_cookie_even_when_access_token_is_invalid(self) -> None:
        token = Token(b"EXPIRED")
        self.token_handler.get_token_remaining_seconds.side_effect = UnauthorizedError

        await self.use_case.logout(
            params=AuthLogoutParams(
                token=token,
                session_secret=SessionSecret("session-secret"),
            ),
        )

        self.session_secret_generator.hash_secret.assert_called_once_with(
            secret=SessionSecret("session-secret"),
        )
        self.session_storage.revoke_session_by_secret_hash.assert_called_once_with(
            secret_hash=SessionSecretHash("session-secret-hash"),
        )
        self.token_revocation_storage.revoke_token.assert_not_called()
