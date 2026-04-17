from itertools import count
from unittest.mock import Mock

from dishka import Provider, provide, Scope

from core.competency_matrix.generators import ItemIdGenerator, ResourceIdGenerator
from core.competency_matrix.use_cases import (
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
    AbstractGetItemUseCase,
    AbstractUpsertItemUseCase,
    AbstractDeleteItemUseCase,
    AbstractPublishSwitchItemUseCase,
    AbstractFindResourcesUseCase,
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

    @provide(scope=Scope.APP)
    async def provide_create_item_use_case(self) -> AbstractUpsertItemUseCase:
        mock = Mock(spec=AbstractUpsertItemUseCase)
        return mock

    @provide(scope=Scope.APP)
    async def provide_delete_item_use_case(self) -> AbstractDeleteItemUseCase:
        mock = Mock(spec=AbstractDeleteItemUseCase)
        return mock

    @provide(scope=Scope.APP)
    async def provide_publish_switch_item_use_case(self) -> AbstractPublishSwitchItemUseCase:
        mock = Mock(spec=AbstractPublishSwitchItemUseCase)
        return mock

    @provide(scope=Scope.APP)
    async def provide_search_resources_use_case(self) -> AbstractFindResourcesUseCase:
        mock = Mock(spec=AbstractFindResourcesUseCase)
        return mock
