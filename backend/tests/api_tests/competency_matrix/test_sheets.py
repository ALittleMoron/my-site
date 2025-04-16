import pytest_asyncio
from verbose_http_exceptions import status

from tests.fixtures import ApiFixture


class TestSheetsAPI(ApiFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.app.get_mock_list_sheets_use_case()

    def test_list(self) -> None:
        self.use_case.sheets = ["Python", "SQL"]
        response = self.api.get_competency_matrix_sheets()
        assert response.status_code == status.HTTP_200_OK, response.content
        assert response.json() == {"sheets": ["Python", "SQL"]}
