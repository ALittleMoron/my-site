from unittest.mock import AsyncMock

import pytest_asyncio

from core.users.exceptions import UserNotFoundError
from core.users.schemas import User, RoleEnum
from entrypoints.auth.backends import (
    BaseAuthenticationBackend,
    AdminAuthenticationBackend,
    UserAuthenticationBackend,
)
from entrypoints.auth.schemas import Payload
from tests.fixtures import FactoryFixture, ContainerFixture


class AnyPermissionsBackend(BaseAuthenticationBackend):
    def check_permission(self, user: User) -> bool:
        _ = user
        return True


class TestAnyPermissionsBackend(ContainerFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.backend = AnyPermissionsBackend(secret_key="")
        hasher = await self.container.get_hasher()
        self.user_1 = self.factory.core.user(
            username="user1",
            password=hasher.hash_password("1111"),
            role=RoleEnum.USER,
        )
        self.user_2 = self.factory.core.user(
            username="user2",
            password=hasher.hash_password("1234"),
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
        auth_handler = await self.container.get_auth_handler()
        token = auth_handler.encode_token(
            payload=Payload(username="not_presented", role=RoleEnum.ADMIN),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is False

    async def test_authenticate(self) -> None:
        auth_handler = await self.container.get_auth_handler()
        self.storage.get_user_by_username.return_value = self.user_1
        token = auth_handler.encode_token(
            payload=Payload(username=self.user_1.username, role=self.user_1.role),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is True
        assert "token" in self.request.session
        assert self.request.session["token"] != str(token)


class TestAdminAuthenticationBackend(ContainerFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        hasher = await self.container.get_hasher()
        self.backend = AdminAuthenticationBackend(secret_key="")
        self.user = self.factory.core.user(
            username="user1",
            password=hasher.hash_password("1111"),
            role=RoleEnum.USER,
        )
        self.storage = await self.container.get_auth_storage()
        self.storage.get_user_by_username.return_value = self.user
        self.request = AsyncMock()
        self.request.state.dishka_container = self.container.container

    async def test_authenticate_user_not_admin(self) -> None:
        auth_handler = await self.container.get_auth_handler()
        token = auth_handler.encode_token(
            payload=Payload(username=self.user.username, role=self.user.role),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is False


class TestUserAuthenticationBackend(ContainerFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.backend = UserAuthenticationBackend(secret_key="")
        hasher = await self.container.get_hasher()
        self.user = self.factory.core.user(
            username="user1",
            password=hasher.hash_password("1111"),
            role=RoleEnum.ADMIN,
        )
        self.storage = await self.container.get_auth_storage()
        self.storage.get_user_by_username.return_value = self.user
        self.request = AsyncMock()
        self.request.state.dishka_container = self.container.container

    async def test_authenticate_user_not_user(self) -> None:
        auth_handler = await self.container.get_auth_handler()
        token = auth_handler.encode_token(
            payload=Payload(username=self.user.username, role=self.user.role),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is False
