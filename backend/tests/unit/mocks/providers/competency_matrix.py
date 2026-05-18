from itertools import count
from unittest.mock import Mock

from dishka import Provider, Scope, provide

from core.competency_matrix.generators import ItemIdGenerator, ResourceIdGenerator
from core.competency_matrix.use_cases import (
    AbstractDeleteItemUseCase,
    AbstractFindResourcesUseCase,
    AbstractGetItemUseCase,
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
    AbstractPublishSwitchItemUseCase,
    AbstractUpsertItemUseCase,
)

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
    async def provide_list_items_use_case(self) -> AbstractListItemsUseCase:
        return Mock(spec=AbstractListItemsUseCase)

    @provide(scope=Scope.APP)
    async def provide_list_sheets_use_case(self) -> AbstractListSheetsUseCase:
        return Mock(spec=AbstractListSheetsUseCase)

    @provide(scope=Scope.APP)
    async def provide_get_item_use_case(self) -> AbstractGetItemUseCase:
        return Mock(spec=AbstractGetItemUseCase)

    @provide(scope=Scope.APP)
    async def provide_create_item_use_case(self) -> AbstractUpsertItemUseCase:
        return Mock(spec=AbstractUpsertItemUseCase)

    @provide(scope=Scope.APP)
    async def provide_delete_item_use_case(self) -> AbstractDeleteItemUseCase:
        return Mock(spec=AbstractDeleteItemUseCase)

    @provide(scope=Scope.APP)
    async def provide_publish_switch_item_use_case(self) -> AbstractPublishSwitchItemUseCase:
        return Mock(spec=AbstractPublishSwitchItemUseCase)

    @provide(scope=Scope.APP)
    async def provide_search_resources_use_case(self) -> AbstractFindResourcesUseCase:
        return Mock(spec=AbstractFindResourcesUseCase)
