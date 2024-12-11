import pytest_asyncio
from httpx import codes

from tests.fixtures import ApiFixture, FactoryFixture, StorageFixture


class TestCompetencyMatrixSheet(ApiFixture, FactoryFixture, StorageFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="function")
    async def setup(self) -> None:
        await self.storage_helper.insert_sheet(sheet=self.factory.sheet(sheet_id=1, name="Python"))
        await self.storage_helper.insert_sheet(sheet=self.factory.sheet(sheet_id=2, name="PHP"))

    async def test_list(self) -> None:
        response = self.api.list_competency_matrix_sheets()
        assert response.status_code == codes.OK
        assert response.json() == {
            'sheets': [
                {
                    "id": 1,
                    "name": "Python",
                },
                {
                    "id": 2,
                    "name": "PHP",
                },
            ],
        }
