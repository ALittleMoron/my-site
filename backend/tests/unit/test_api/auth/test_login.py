# ruff: noqa: S106
import pytest_asyncio

from core.auth.enums import RoleEnum
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestLoginAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.uuid = await self.container.get_random_uuid()
        self.use_case = await self.container.get_auth_use_case()

    def test_login(self) -> None:
        self.api.post_login(
            data=self.factory.api.login_request(
                username="USERNAME",
                password="PASSWORD",
            ),
        )
        self.use_case.login.assert_called_once_with(
            username="USERNAME",
            password="PASSWORD",
            required_role=RoleEnum.ADMIN,
        )
