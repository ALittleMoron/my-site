# ruff: noqa: S106
from unittest.mock import Mock

import pytest
import pytest_asyncio

from core.auth.enums import RoleEnum
from core.auth.event_dispatchers import AuthEventReporter
from core.auth.exceptions import ForbiddenError, UnauthorizedError, UserNotFoundError
from core.auth.schemas import JwtUser
from core.auth.storages import TokenRevocationStorage
from core.auth.use_cases import AuthUseCase
from tests.test_cases import ContainerTestCase


class TestAuthUseCase(ContainerTestCase):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.hasher = await self.container.get_hasher()
        self.token_handler = await self.container.get_token_handler()
        self.auth_storage = await self.container.get_auth_storage()
        self.token_revocation_storage = Mock(spec=TokenRevocationStorage)
        self.user_storage = await self.container.get_user_storage()
        self.auth_event_reporter = Mock(spec=AuthEventReporter)
        self.use_case = AuthUseCase(
            hasher=self.hasher,
            token_handler=self.token_handler,
            auth_storage=self.auth_storage,
            token_revocation_storage=self.token_revocation_storage,
            user_storage=self.user_storage,
            event_reporter=self.auth_event_reporter,
        )

    async def test_login_user_not_found(self) -> None:
        self.user_storage.get_user_by_username.side_effect = UserNotFoundError
        with pytest.raises(UnauthorizedError):
            await self.use_case.login(
                username="test",
                password="test",
                required_role=RoleEnum.ADMIN,
            )
        self.auth_event_reporter.report_login_user_not_found.assert_called_once_with(
            username="test",
        )

    async def test_login_user_role_not_has_role(self) -> None:
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.USER,
        )
        with pytest.raises(ForbiddenError):
            await self.use_case.login(
                username="test",
                password="test",
                required_role=RoleEnum.ADMIN,
            )
        self.auth_event_reporter.report_login_role_forbidden.assert_called_once_with(
            username="test",
            required_role=RoleEnum.ADMIN,
        )

    async def test_login_not_verified_password(self) -> None:
        self.hasher.verify_password.return_value = (False, False)
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
        )
        with pytest.raises(UnauthorizedError):
            await self.use_case.login(
                username="test",
                password="test",
                required_role=RoleEnum.ADMIN,
            )
        self.auth_event_reporter.report_login_password_verification_failed.assert_called_once_with(
            username="test",
        )

    async def test_login_rehash_on_password_expire(self) -> None:
        self.token_handler.encode_token.return_value = b"TOKEN"
        self.hasher.verify_password.return_value = (True, True)
        self.hasher.hash_password.return_value = "new_password"
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
        )
        token = await self.use_case.login(
            username="test",
            password="test",
            required_role=RoleEnum.ADMIN,
        )
        assert token == self.factory.core.token(b"TOKEN")
        self.auth_storage.update_user_password_hash.assert_called_once_with(
            username="test",
            password_hash="new_password",
        )

    async def test_login(self) -> None:
        self.token_handler.encode_token.return_value = b"TOKEN"
        self.hasher.verify_password.return_value = (True, False)
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
        )
        token = await self.use_case.login(
            username="test",
            password="test",
            required_role=RoleEnum.ADMIN,
        )
        assert token == self.factory.core.token(b"TOKEN")
        self.user_storage.get_user_by_username.assert_called_once_with(username="test")
        self.hasher.verify_password.assert_called_once_with(
            plain_password="test",
            hashed_password="test",
        )
        self.token_handler.encode_token.assert_called_once_with(
            payload=JwtUser(username="test", role=RoleEnum.ADMIN),
        )
