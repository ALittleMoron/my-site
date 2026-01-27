from unittest.mock import Mock

import pytest

from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import ListItemsUseCase
from core.enums import PublishStatusEnum
from tests.fixtures import FactoryFixture


class TestListItemsUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.use_case = ListItemsUseCase(storage=self.storage)

    async def test_not_available(self) -> None:
        self.storage.list_competency_matrix_items.return_value = [
            self.factory.core.competency_matrix_item(
                item_id=1,
                question="1",
                publish_status=PublishStatusEnum.DRAFT,
                sheet="Python",
                grade=None,
                section="",
                subsection="",
            ),
        ]
        items = await self.use_case.execute(sheet_name="Python", only_published=True)
        assert items.values == []

    async def test_available(self) -> None:
        self.storage.list_competency_matrix_items.return_value = [
            self.factory.core.competency_matrix_item(
                item_id=1,
                question="1",
                publish_status=PublishStatusEnum.PUBLISHED,
                sheet="Python",
                grade=GradeEnum.JUNIOR,
                section="1",
                subsection="1",
            ),
        ]
        items = await self.use_case.execute(sheet_name="Python", only_published=True)
        assert items.values == [
            self.factory.core.competency_matrix_item(
                item_id=1,
                question="1",
                publish_status=PublishStatusEnum.PUBLISHED,
                sheet="Python",
                grade=GradeEnum.JUNIOR,
                section="1",
                subsection="1",
            ),
        ]

    async def test_availability_skip(self) -> None:
        self.storage.list_competency_matrix_items.return_value = [
            self.factory.core.competency_matrix_item(
                item_id=1,
                question="1",
                publish_status=PublishStatusEnum.DRAFT,
                sheet="Python",
                grade=None,
                section="",
                subsection="",
            ),
        ]
        items = await self.use_case.execute(sheet_name="Python", only_published=False)
        assert items.values == [
            self.factory.core.competency_matrix_item(
                item_id=1,
                question="1",
                publish_status=PublishStatusEnum.DRAFT,
                sheet="Python",
                grade=None,
                section="",
                subsection="",
            ),
        ]
