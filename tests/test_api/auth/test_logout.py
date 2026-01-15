import pytest_asyncio

from core.auth.types import Token
from tests.fixtures import ApiFixture, FactoryFixture, ContainerFixture


class TestLogoutAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.uuid = await self.container.get_random_uuid()
        self.use_case = await self.container.get_logout_use_case()

    def test_login(self) -> None:
        self.api.post_logout()
        self.use_case.execute.assert_called_once_with(token=Token("token".encode()))
