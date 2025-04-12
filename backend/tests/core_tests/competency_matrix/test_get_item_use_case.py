from datetime import datetime, UTC

import pytest

from core.competency_matrix.enums import StatusEnum
from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.use_cases import GetItemUseCase
from tests.fixtures import FactoryFixture
from tests.mocks.competency_matrix.storages import MockCompetencyMatrixStorage


class TestListItemsUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = MockCompetencyMatrixStorage()
        self.status_changed = datetime.now(tz=UTC)
        self.use_case = GetItemUseCase(storage=self.storage)

    async def test_not_available(self) -> None:
        self.storage.items = [
            self.factory.competency_matrix_item(
                item_id=2,
                question="2",
                status=StatusEnum.DRAFT,
                sheet="Python",
                grade="",
                section="",
                subsection="",
            ),
        ]
        with pytest.raises(CompetencyMatrixItemNotFoundError):
            await self.use_case.execute(item_id=2)

    async def test_available(self) -> None:
        self.storage.items = [
            self.factory.competency_matrix_item(
                item_id=1,
                question="1",
                status=StatusEnum.PUBLISHED,
                sheet="Python",
                grade="1",
                section="1",
                subsection="1",
                status_changed=self.status_changed,
            ),
        ]
        item = await self.use_case.execute(item_id=1)
        assert item == self.factory.competency_matrix_item(
            item_id=1,
            question="1",
            status=StatusEnum.PUBLISHED,
            sheet="Python",
            grade="1",
            section="1",
            subsection="1",
            status_changed=self.status_changed,
        )
