import pytest_asyncio
from httpx import codes

from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestFindResourcesAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_competency_matrix_use_case()

    def test_search_resources(self) -> None:
        response = self.api.get_search_competency_matrix_resources(search_name="test")
        assert response.status_code == codes.OK
        self.use_case.find_resources.assert_called_once_with(
            search_name=self.factory.core.search_name("test"),
        )
