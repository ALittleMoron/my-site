import pytest

from core.competency_matrix.use_cases import ListSheetsUseCase
from tests.fixtures import FactoryFixture
from tests.mocks.competency_matrix.storages import MockCompetencyMatrixStorage


class TestListSheetsUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = MockCompetencyMatrixStorage()
        self.use_case = ListSheetsUseCase(storage=self.storage)

    async def test_list_sheets(self) -> None:
        self.storage.sheets = ["Python", "SQL"]
        sheets = await self.use_case.execute()
        assert sheets == self.factory.sheets(values=["Python", "SQL"])
