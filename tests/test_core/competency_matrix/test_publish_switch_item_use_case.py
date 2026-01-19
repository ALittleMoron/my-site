from unittest.mock import Mock

import pytest

from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import PublishSwitchItemUseCase
from core.enums import PublishStatusEnum
from tests.fixtures import FactoryFixture


class TestPublishSwitchItemUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.use_case = PublishSwitchItemUseCase(storage=self.storage)

    async def test_set_draft(self) -> None:
        self.storage.get_competency_matrix_item.return_value = (
            self.factory.core.competency_matrix_item(
                item_id=1,
                publish_status=PublishStatusEnum.PUBLISHED,
            )
        )
        await self.use_case.execute(
            item_id=self.factory.core.int_id(1),
            publish_status=PublishStatusEnum.DRAFT,
        )
        self.storage.get_competency_matrix_item.assert_called_once_with(
            item_id=self.factory.core.int_id(1),
        )
        self.storage.upsert_competency_matrix_item.assert_called_once_with(
            item=self.factory.core.competency_matrix_item(
                item_id=1,
                publish_status=PublishStatusEnum.DRAFT,
            )
        )

    async def test_set_published(self) -> None:
        self.storage.get_competency_matrix_item.return_value = (
            self.factory.core.competency_matrix_item(
                item_id=1,
                publish_status=PublishStatusEnum.DRAFT,
            )
        )
        await self.use_case.execute(
            item_id=self.factory.core.int_id(1),
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        self.storage.get_competency_matrix_item.assert_called_once_with(
            item_id=self.factory.core.int_id(1),
        )
        self.storage.upsert_competency_matrix_item.assert_called_once_with(
            item=self.factory.core.competency_matrix_item(
                item_id=1,
                publish_status=PublishStatusEnum.PUBLISHED,
            )
        )
