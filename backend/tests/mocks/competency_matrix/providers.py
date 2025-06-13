from unittest.mock import Mock

from dishka import provide, Scope, Provider

from core.competency_matrix.use_cases import (
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
    AbstractGetItemUseCase,
)


class MockCompetencyMatrixProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_list_items_use_case(self) -> AbstractListItemsUseCase:
        mock = Mock(spec=AbstractListItemsUseCase)
        return mock

    @provide(scope=Scope.APP)
    async def provide_list_sheets_use_case(self) -> AbstractListSheetsUseCase:
        mock = Mock(spec=AbstractListSheetsUseCase)
        return mock

    @provide(scope=Scope.APP)
    async def provide_get_item_use_case(self) -> AbstractGetItemUseCase:
        mock = Mock(spec=AbstractGetItemUseCase)
        return mock
