from unittest.mock import AsyncMock

import pytest_asyncio

from core.auth.enums import RoleEnum
from entrypoints.admin.auth_backends import AdminAuthenticationBackend
from tests.fixtures import FactoryFixture, ContainerFixture


class TestAdminAuthenticationBackend(ContainerFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.backend = AdminAuthenticationBackend(secret_key="")
        self.hasher = await self.container.get_hasher()
        self.auth_handler = await self.container.get_token_handler()
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
        self.login_use_case = await self.container.get_login_use_case()
        self.authenticate_use_case = await self.container.get_authenticate_use_case()
        self.request = AsyncMock()
        self.request.state.dishka_container = self.container.container
        self.request.session = {}

    async def test_login_incorrect_input_data(self) -> None:
        self.request.form = AsyncMock(return_value={"username": 123, "password": 123})
        assert (await self.backend.login(request=self.request)) is False

    async def test_login_fail(self) -> None:
        self.login_use_case.execute.return_value = None
        assert (await self.backend.login(request=self.request)) is False

    async def test_login(self) -> None:
        self.login_use_case.execute.return_value = "TOKEN".encode()
        self.request.form = AsyncMock(return_value={"username": "user2", "password": "1234"})
        self.request.session = {}
        assert (await self.backend.login(request=self.request)) is True
        assert "token" in self.request.session
        assert self.request.session["token"] == "TOKEN"

    async def test_logout(self) -> None:
        self.request.session = {"token": "some_token"}
        assert (await self.backend.logout(request=self.request)) is True
        assert self.request.session == {}

    async def test_authenticate_fail(self) -> None:
        self.authenticate_use_case.execute.return_value = None
        assert (await self.backend.authenticate(request=self.request)) is False

    async def test_authenticate(self) -> None:
        self.authenticate_use_case.execute.return_value = "NEW_TOKEN".encode()
        self.request.session = {"token": "TOKEN"}
        assert (await self.backend.authenticate(request=self.request)) is True
        assert "token" in self.request.session
        assert self.request.session["token"] != "TOKEN"
