from unittest.mock import Mock

import pytest

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import GetItemUseCase
from core.enums import PublishStatusEnum
from tests.fixtures import FactoryFixture


class TestGetItemUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.use_case = GetItemUseCase(storage=self.storage)

    async def test_not_available(self) -> None:
        item = self.factory.core.competency_matrix_item(
            item_id=2,
            question="2",
            publish_status=PublishStatusEnum.DRAFT,
            sheet="Python",
            grade="",
            section="",
            subsection="",
        )
        self.storage.get_competency_matrix_item.return_value = item
        with pytest.raises(CompetencyMatrixItemNotFoundError):
            await self.use_case.execute(
                item_id=self.factory.core.int_id(2),
                only_published=True,
            )

    async def test_available(self) -> None:
        item = self.factory.core.competency_matrix_item(
            item_id=1,
            question="1",
            publish_status=PublishStatusEnum.PUBLISHED,
            sheet="Python",
            grade="1",
            section="1",
            subsection="1",
        )
        self.storage.get_competency_matrix_item.return_value = item
        res_item = await self.use_case.execute(
            item_id=self.factory.core.int_id(1),
            only_published=True,
        )
        assert item == res_item

    async def test_availability_skip(self) -> None:
        item = self.factory.core.competency_matrix_item(
            item_id=1,
            question="1",
            publish_status=PublishStatusEnum.DRAFT,
            sheet="Python",
            grade="",
            section="",
            subsection="",
        )
        self.storage.get_competency_matrix_item.return_value = item
        res_item = await self.use_case.execute(
            item_id=self.factory.core.int_id(1),
            only_published=False,
        )
        assert item == res_item
