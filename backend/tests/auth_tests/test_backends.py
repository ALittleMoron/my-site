from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest_asyncio
from dishka import AsyncContainer

from core.users.schemas import User, RoleEnum
from entrypoints.auth.backends import (
    BaseAuthenticationBackend,
    AdminAuthenticationBackend,
    UserAuthenticationBackend,
)
from entrypoints.auth.handlers import AuthHandler
from entrypoints.auth.schemas import Payload
from entrypoints.auth.utils import Hasher
from tests.fixtures import FactoryFixture
from tests.mocks.auth.providers import users


class AnyPermissionsBackend(BaseAuthenticationBackend):
    def check_permission(self, user: User) -> bool:
        _ = user
        return True


class TestAnyPermissionsBackend(FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self, container: AsyncContainer) -> AsyncGenerator[None, None]:
        self.container = container
        self.backend = AnyPermissionsBackend(secret_key="")
        hasher = await container.get(Hasher)
        # TODO: optimize users. It very slow
        users.extend(
            [
                self.factory.user(
                    username="user1",
                    password=hasher.hash_password("1111"),
                    role=RoleEnum.USER,
                ),
                self.factory.user(
                    username="user2",
                    password=hasher.hash_password("1234"),
                    role=RoleEnum.ADMIN,
                ),
            ]
        )
        self.request = AsyncMock()
        async with container() as request_container:
            self.request.state.dishka_container = request_container
            yield
        users.clear()

    async def test_login_incorrect_input_data(self) -> None:
        self.request.form = AsyncMock(return_value={"username": 123, "password": 123})
        assert (await self.backend.login(request=self.request)) is False

    async def test_login_user_not_found(self) -> None:
        self.request.form = AsyncMock(return_value={"username": "NOT_FOUND", "password": "1234"})
        assert (await self.backend.login(request=self.request)) is False

    async def test_login_password_not_suit(self) -> None:
        self.request.form = AsyncMock(return_value={"username": "user1", "password": "1234"})
        assert (await self.backend.login(request=self.request)) is False

    async def test_login(self) -> None:
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
        auth_handler = await self.container.get(AuthHandler)
        token = auth_handler.encode_token(
            payload=Payload(username="not_presented", role=RoleEnum.ADMIN),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is False

    async def test_authenticate(self) -> None:
        auth_handler = await self.container.get(AuthHandler)
        user = users[1]
        token = auth_handler.encode_token(
            payload=Payload(username=user.username, role=user.role),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is True
        assert "token" in self.request.session
        assert self.request.session["token"] != str(token)


class TestAdminAuthenticationBackend(FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self, container: AsyncContainer) -> AsyncGenerator[None, None]:
        self.container = container
        self.backend = AdminAuthenticationBackend(secret_key="")
        hasher = await container.get(Hasher)
        # TODO: optimize users. It very slow
        users.append(
            self.factory.user(
                username="user1",
                password=hasher.hash_password("1111"),
                role=RoleEnum.USER,
            ),
        )
        self.request = AsyncMock()
        async with container() as request_container:
            self.request.state.dishka_container = request_container
            yield
        users.clear()

    async def test_authenticate_user_not_admin(self) -> None:
        auth_handler = await self.container.get(AuthHandler)
        user = users[0]
        token = auth_handler.encode_token(
            payload=Payload(username=user.username, role=user.role),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is False


class TestUserAuthenticationBackend(FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self, container: AsyncContainer) -> AsyncGenerator[None, None]:
        self.container = container
        self.backend = UserAuthenticationBackend(secret_key="")
        hasher = await container.get(Hasher)
        # TODO: optimize users. It very slow
        users.append(
            self.factory.user(
                username="user1",
                password=hasher.hash_password("1111"),
                role=RoleEnum.ADMIN,
            ),
        )
        self.request = AsyncMock()
        async with container() as request_container:
            self.request.state.dishka_container = request_container
            yield
        users.clear()

    async def test_authenticate_user_not_user(self) -> None:
        auth_handler = await self.container.get(AuthHandler)
        user = users[0]
        token = auth_handler.encode_token(
            payload=Payload(username=user.username, role=user.role),
        )
        self.request.session = {"token": token.decode()}
        assert (await self.backend.authenticate(request=self.request)) is False
