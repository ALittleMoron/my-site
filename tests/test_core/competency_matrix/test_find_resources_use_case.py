from unittest.mock import Mock

import pytest

from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import FindResourcesUseCase
from tests.fixtures import FactoryFixture


class TestFindResourcesItemUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.use_case = FindResourcesUseCase(storage=self.storage)

    async def test_search_resources(self) -> None:
        search_name = self.factory.core.search_name("Find")
        await self.use_case.execute(search_name=search_name)
        self.storage.search_competency_matrix_resources.assert_called_once_with(
            search_name="find",
        )
