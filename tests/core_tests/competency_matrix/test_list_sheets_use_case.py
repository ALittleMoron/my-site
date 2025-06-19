from unittest.mock import Mock

import pytest

from core.competency_matrix.use_cases import ListSheetsUseCase
from db.storages.competency_matrix import CompetencyMatrixStorage
from tests.fixtures import FactoryFixture


class TestListSheetsUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.use_case = ListSheetsUseCase(storage=self.storage)

    async def test_list_sheets(self) -> None:
        self.storage.list_sheets.return_value = ["Python", "SQL"]
        sheets = await self.use_case.execute()
        assert sheets == self.factory.core.sheets(values=["Python", "SQL"])
