import pytest_asyncio

from core.auth.types import Token
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestLogoutAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.uuid = await self.container.get_random_uuid()
        self.use_case = await self.container.get_auth_use_case()

    def test_login(self) -> None:
        self.api.post_logout()
        self.use_case.logout.assert_called_once_with(token=Token(b"token"))
