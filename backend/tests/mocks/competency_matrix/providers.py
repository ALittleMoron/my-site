from dishka import provide, Scope, Provider, alias

from core.competency_matrix.use_cases import (
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
    AbstractGetItemUseCase,
)
from tests.mocks.competency_matrix.use_cases import (
    MockGetItemUseCase,
    MockListSheetsUseCase,
    MockListItemsUseCase,
)


class MockCompetencyMatrixProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_list_items_use_case(self) -> AbstractListItemsUseCase:
        return MockListItemsUseCase()

    @provide(scope=Scope.APP)
    async def provide_list_sheets_use_case(self) -> AbstractListSheetsUseCase:
        return MockListSheetsUseCase()

    @provide(scope=Scope.APP)
    async def provide_get_item_use_case(self) -> AbstractGetItemUseCase:
        return MockGetItemUseCase()

    provide_list_items_use_case_alias = alias(
        source=AbstractListItemsUseCase,
        provides=MockListItemsUseCase,
    )
    provide_list_sheets_use_case_alias = alias(
        source=AbstractListSheetsUseCase,
        provides=MockListSheetsUseCase,
    )
    provide_get_item_use_case_alias = alias(
        source=AbstractGetItemUseCase,
        provides=MockGetItemUseCase,
    )
