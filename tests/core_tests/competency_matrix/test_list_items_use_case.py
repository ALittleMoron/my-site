from unittest.mock import Mock

import pytest

from core.competency_matrix.enums import StatusEnum
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import ListItemsUseCase
from tests.fixtures import FactoryFixture


class TestListItemsUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.use_case = ListItemsUseCase(storage=self.storage)

    async def test_filter_available(self) -> None:
        self.storage.list_competency_matrix_items.return_value = [
            self.factory.core.competency_matrix_item(
                # available
                item_id=1,
                question="1",
                status=StatusEnum.PUBLISHED,
                sheet="Python",
                grade="1",
                section="1",
                subsection="1",
            ),
            self.factory.core.competency_matrix_item(
                # Not available
                item_id=2,
                question="2",
                status=StatusEnum.DRAFT,
                sheet="Python",
                grade="",
                section="",
                subsection="",
            ),
        ]
        items = await self.use_case.execute(sheet_name="Python")
        assert len(items) == 1
        assert items[0].id == 1
