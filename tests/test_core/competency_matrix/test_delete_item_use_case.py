from unittest.mock import Mock

import pytest

from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import DeleteItemUseCase
from tests.fixtures import FactoryFixture


class TestDeleteItemUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.use_case = DeleteItemUseCase(storage=self.storage)

    async def test_delete(self) -> None:
        item_id = self.factory.core.int_id(1)
        await self.use_case.execute(item_id=item_id)
        self.storage.delete_competency_matrix_item.assert_called_once_with(item_id=item_id)
