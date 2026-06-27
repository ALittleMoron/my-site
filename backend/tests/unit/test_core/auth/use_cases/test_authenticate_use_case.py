# ruff: noqa: S106
from unittest.mock import Mock

import pytest
import pytest_asyncio

from core.auth.enums import RoleEnum
from core.auth.event_dispatchers import AuthEventReporter
from core.auth.exceptions import ForbiddenError, UnauthorizedError, UserNotFoundError
from core.auth.storages import TokenRevocationStorage
from core.auth.types import Token
from core.auth.use_cases import AuthUseCase
from tests.test_cases import ContainerTestCase


class TestLoginUseCase(ContainerTestCase):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.token_handler = await self.container.get_token_handler()
        self.user_storage = await self.container.get_user_storage()
        self.token_revocation_storage = Mock(spec=TokenRevocationStorage)
        self.token_revocation_storage.is_token_revoked.return_value = False
        self.auth_event_reporter = Mock(spec=AuthEventReporter)
        self.use_case = AuthUseCase(
            hasher=await self.container.get_hasher(),
            auth_storage=await self.container.get_auth_storage(),
            token_handler=self.token_handler,
            token_revocation_storage=self.token_revocation_storage,
            user_storage=self.user_storage,
            event_reporter=self.auth_event_reporter,
        )

    async def test_authenticate_revoked_token(self) -> None:
        token = Token(b"revoked_token")
        self.token_revocation_storage.is_token_revoked.return_value = True

        with pytest.raises(UnauthorizedError):
            await self.use_case.authenticate(
                token=token,
                required_role=RoleEnum.ADMIN,
            )

        self.token_revocation_storage.is_token_revoked.assert_called_once_with(token=token)
        self.token_handler.decode_token.assert_not_called()
        self.user_storage.get_user_by_username.assert_not_called()
        self.auth_event_reporter.report_authentication_revoked_token_used.assert_called_once_with()

    async def test_authenticate_token_decode_error(self) -> None:
        self.token_handler.decode_token.side_effect = UnauthorizedError
        with pytest.raises(UnauthorizedError):
            await self.use_case.authenticate(
                token=Token(b"invalid_token"),
                required_role=RoleEnum.ADMIN,
            )
        self.token_revocation_storage.is_token_revoked.assert_called_once_with(
            token=Token(b"invalid_token"),
        )
        self.token_handler.decode_token.assert_called_once_with(b"invalid_token")

    async def test_authenticate_user_not_found(self) -> None:
        self.user_storage.get_user_by_username.side_effect = UserNotFoundError
        self.token_handler.decode_token.return_value = self.factory.core.jwt_user(
            username="test",
            role=RoleEnum.ADMIN,
        )
        with pytest.raises(UnauthorizedError):
            await self.use_case.authenticate(
                token=Token(b"valid_token"),
                required_role=RoleEnum.ADMIN,
            )
        self.user_storage.get_user_by_username.assert_called_once_with(username="test")
        self.auth_event_reporter.report_authentication_user_not_found.assert_called_once_with(
            username="test",
        )

    async def test_authenticate_user_not_has_role(self) -> None:
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.USER,
        )
        self.token_handler.decode_token.return_value = self.factory.core.jwt_user(
            username="test",
            role=RoleEnum.USER,
        )
        with pytest.raises(ForbiddenError):
            await self.use_case.authenticate(
                token=Token(b"valid_token"),
                required_role=RoleEnum.ADMIN,
            )
        self.auth_event_reporter.report_authentication_role_forbidden.assert_called_once_with(
            username="test",
            required_role=RoleEnum.ADMIN,
        )

    async def test_authenticate_inactive_user(self) -> None:
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
            is_active=False,
        )
        self.token_handler.decode_token.return_value = self.factory.core.jwt_user(
            username="test",
            role=RoleEnum.ADMIN,
        )

        with pytest.raises(UnauthorizedError):
            await self.use_case.authenticate(
                token=Token(b"valid_token"),
                required_role=RoleEnum.ADMIN,
            )

        self.auth_event_reporter.report_authentication_inactive_user.assert_called_once_with(
            username="test",
        )

    async def test_authenticate(self) -> None:
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
        )
        self.token_handler.decode_token.return_value = self.factory.core.jwt_user(
            username="test",
            role=RoleEnum.ADMIN,
        )
        self.token_handler.encode_token.return_value = b"NEW_TOKEN"
        user = await self.use_case.authenticate(
            token=Token(b"valid_token"),
            required_role=RoleEnum.ADMIN,
        )
        assert user == self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
        )
