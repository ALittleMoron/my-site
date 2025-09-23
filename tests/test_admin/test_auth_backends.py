from unittest.mock import AsyncMock

import pytest_asyncio

from core.auth.enums import RoleEnum
from core.auth.exceptions import UserNotFoundError
from core.auth.schemas import AuthTokenPayload
from entrypoints.admin.auth_backends import AdminAuthenticationBackend
from tests.fixtures import FactoryFixture, ContainerFixture


class TestAnyPermissionsBackend(ContainerFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.backend = AdminAuthenticationBackend(secret_key="")
        self.hasher = await self.container.get_hasher()
        self.auth_handler = await self.container.get_auth_handler()
        self.user_1 = self.factory.core.user(
            username="user1",
            password_hash="1111",
            role=RoleEnum.USER,
        )
        self.user_2 = self.factory.core.user(
            username="user2",
            password_hash="1234",
            role=RoleEnum.ADMIN,
        )
        self.storage = await self.container.get_auth_storage()
        self.request = AsyncMock()
        self.request.state.dishka_container = self.container.container

    async def test_login_incorrect_input_data(self) -> None:
        self.request.form = AsyncMock(return_value={"username": 123, "password": 123})
        assert (await self.backend.login(request=self.request)) is False

    async def test_login_user_not_found(self) -> None:
        self.storage.get_user_by_username.side_effect = UserNotFoundError()
        self.request.form = AsyncMock(return_value={"username": "NOT_FOUND", "password": "1234"})
        assert (await self.backend.login(request=self.request)) is False

    async def test_login_password_not_suit(self) -> None:
        self.storage.get_user_by_username.return_value = self.user_1
        self.request.form = AsyncMock(return_value={"username": "user1", "password": "1234"})
        assert (await self.backend.login(request=self.request)) is False

    async def test_login_password_not_verified_password(self) -> None:
        self.hasher.verify_password.return_value = False, False
        self.storage.get_user_by_username.return_value = self.user_2
        self.request.form = AsyncMock(return_value={"username": "user2", "password": "1234"})
        self.request.session = {}
        assert (await self.backend.login(request=self.request)) is False

    async def test_login_password_need_rehash(self) -> None:
        self.hasher.verify_password.return_value = True, True
        self.storage.get_user_by_username.return_value = self.user_2
        self.request.form = AsyncMock(return_value={"username": "user2", "password": "1234"})
        self.request.session = {}
        await self.backend.login(request=self.request)
        self.storage.update_user_password_hash.assert_called_once_with(
            username="user2",
            password_hash="1234",
        )

    async def test_login(self) -> None:
        self.storage.get_user_by_username.return_value = self.user_2
        self.request.form = AsyncMock(return_value={"username": "user2", "password": "1234"})
        self.request.session = {}
        assert (await self.backend.login(request=self.request)) is True
        assert "token" in self.request.session

    async def test_logout(self) -> None:
        self.request.session = {"token": "some_token"}
        assert (await self.backend.logout(request=self.request)) is True
        assert self.request.session == {}

    async def test_authenticate_no_token(self) -> None:
        self.request.session = {}
        assert (await self.backend.authenticate(request=self.request)) is False

    async def test_authenticate_token_is_not_str(self) -> None:
        self.request.session = {"token": 25}
        assert (await self.backend.authenticate(request=self.request)) is False

    async def test_authenticate_token_decode_error(self) -> None:
        self.request.session = {"token": "v3.local.asgatawtrwkjrwarakw"}
        assert (await self.backend.authenticate(request=self.request)) is False

    async def test_authenticate_user_not_found(self) -> None:
        self.storage.get_user_by_username.side_effect = UserNotFoundError()
        token = self.auth_handler.encode_token(
            payload=AuthTokenPayload(username="not_presented", role=RoleEnum.ADMIN),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is False

    async def test_authenticate_user_not_admin(self) -> None:
        self.storage.get_user_by_username.return_value = self.user_1
        token = self.auth_handler.encode_token(
            payload=AuthTokenPayload(username=self.user_1.username, role=self.user_1.role),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is False

    async def test_authenticate(self) -> None:
        self.storage.get_user_by_username.return_value = self.user_2
        token = self.auth_handler.encode_token(
            payload=AuthTokenPayload(username=self.user_2.username, role=self.user_2.role),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is True
        assert "token" in self.request.session
        assert self.request.session["token"] != str(token)


class TestAdminAuthenticationBackend(ContainerFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.backend = AdminAuthenticationBackend(secret_key="")
        self.hasher = await self.container.get_hasher()
        self.auth_handler = await self.container.get_auth_handler()
        self.user = self.factory.core.user(
            username="user1",
            password_hash=self.hasher.hash_password("1111"),
            role=RoleEnum.USER,
        )
        self.storage = await self.container.get_auth_storage()
        self.storage.get_user_by_username.return_value = self.user
        self.request = AsyncMock()
        self.request.state.dishka_container = self.container.container

    async def test_authenticate_user_not_admin(self) -> None:
        token = self.auth_handler.encode_token(
            payload=AuthTokenPayload(username=self.user.username, role=self.user.role),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is False
