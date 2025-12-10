from unittest.mock import AsyncMock

import pytest_asyncio

from config.settings import Settings
from core.auth.enums import RoleEnum
from entrypoints.admin.auth_backends import AdminAuthenticationBackend, SessionConfig
from tests.fixtures import FactoryFixture, ContainerFixture


class TestAdminAuthenticationBackend(ContainerFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self, test_settings: Settings) -> None:
        self.backend = AdminAuthenticationBackend(session_config=SessionConfig(secret_key=""))
        self.hasher = await self.container.get_hasher()
        self.token_handler = await self.container.get_token_handler()
        self.storage = await self.container.get_auth_storage()
        self.request = AsyncMock()
        self.request.state.dishka_container = self.container.container
        self.request.session = {}
        self.username = test_settings.admin.init_username
        self.password = test_settings.admin.init_password.get_secret_value()

    async def test_login_incorrect_input_data(self) -> None:
        self.request.form = AsyncMock(return_value={"username": 123, "password": 123})
        assert (await self.backend.login(request=self.request)) is False

    async def test_login_fail(self) -> None:
        self.request.form = AsyncMock(
            return_value={"username": "NOT_KNOWN", "password": "NOT_SUIT"}
        )
        assert (await self.backend.login(request=self.request)) is False

    async def test_login(self) -> None:
        self.token_handler.encode_token.return_value = b"1234"
        self.request.form = AsyncMock(
            return_value={"username": self.username, "password": self.password},
        )
        self.request.session = {}
        assert (await self.backend.login(request=self.request)) is True
        assert "token" in self.request.session
        assert self.request.session["token"] == "1234"
        self.token_handler.encode_token.assert_called_once_with(
            payload=self.factory.core.auth_token_payload(
                username=self.username,
                role=RoleEnum.ADMIN,
            )
        )

    async def test_logout(self) -> None:
        self.request.session = {"token": "some_token"}
        assert (await self.backend.logout(request=self.request)) is True
        assert self.request.session == {}

    async def test_authenticate_fail(self) -> None:
        assert (await self.backend.authenticate(request=self.request)) is False

    async def test_authenticate(self) -> None:
        self.token_handler.encode_token.return_value = b"1234"
        self.token_handler.decode_token.return_value = self.factory.core.auth_token_payload(
            username=self.username,
            role=RoleEnum.ADMIN,
        )
        self.request.session = {"token": "TOKEN"}
        assert (await self.backend.authenticate(request=self.request)) is True
        assert "token" in self.request.session
        assert self.request.session["token"] == "1234"
        self.token_handler.decode_token.assert_called_once_with(b"TOKEN")
        self.token_handler.encode_token.assert_called_once_with(
            payload=self.factory.core.auth_token_payload(
                username=self.username,
                role=RoleEnum.ADMIN,
            )
        )
