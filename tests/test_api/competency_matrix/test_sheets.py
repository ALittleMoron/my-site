import pytest_asyncio
from httpx import codes

from tests.fixtures import ApiFixture, FactoryFixture, ContainerFixture


class TestSheetsAPI(ContainerFixture, FactoryFixture, ApiFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_list_sheets_use_case()

    def test_list(self) -> None:
        self.use_case.execute.return_value = self.factory.core.sheets(values=["Python", "SQL"])
        response = self.api.get_competency_matrix_sheets()
        assert response.status_code == codes.OK, response.content
        assert response.json() == {"sheets": ["Python", "SQL"]}
