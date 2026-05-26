from itertools import count
from unittest.mock import Mock

from dishka import Provider, Scope, provide

from core.competency_matrix.generators import ItemIdGenerator, ResourceIdGenerator
from core.competency_matrix.use_cases import AbstractCompetencyMatrixUseCase

item_id_generator = count(1)
resource_id_generator = count(1)


class MockCompetencyMatrixProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_item_id_generator(self) -> ItemIdGenerator:
        mock = Mock(spec=ItemIdGenerator)
        mock.get_next = lambda: next(item_id_generator)
        return mock

    @provide(scope=Scope.APP)
    async def provide_resource_id_generator(self) -> ResourceIdGenerator:
        mock = Mock(spec=ResourceIdGenerator)
        mock.get_next = lambda: next(resource_id_generator)
        return mock

    @provide(scope=Scope.APP)
    async def provide_competency_matrix_use_case(self) -> AbstractCompetencyMatrixUseCase:
        return Mock(spec=AbstractCompetencyMatrixUseCase)
