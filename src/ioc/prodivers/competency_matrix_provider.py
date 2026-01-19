from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.competency_matrix.generators import ItemIdGenerator, ResourceIdGenerator
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import (
    AbstractDeleteItemUseCase,
    AbstractGetItemUseCase,
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
    AbstractUpsertItemUseCase,
    DeleteItemUseCase,
    GetItemUseCase,
    ListItemsUseCase,
    ListSheetsUseCase,
    UpsertItemUseCase,
)
from db.storages.competency_matrix import CompetencyMatrixDatabaseStorage
from entrypoints.litestar.views.competency_matrix.context_converters import (
    CompetencyMatrixContextConverter,
)


class CompetencyMatrixProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_item_id_generator(self) -> ItemIdGenerator:
        return ItemIdGenerator()

    @provide(scope=Scope.APP)
    async def provide_resource_id_generator(self) -> ResourceIdGenerator:
        return ResourceIdGenerator()

    @provide(scope=Scope.APP)
    async def provide_context_converter(self) -> CompetencyMatrixContextConverter:
        return CompetencyMatrixContextConverter()

    @provide(scope=Scope.REQUEST)
    async def provide_competency_matrix_storage(
        self,
        session: AsyncSession,
    ) -> CompetencyMatrixStorage:
        return CompetencyMatrixDatabaseStorage(session=session)

    @provide(scope=Scope.REQUEST)
    async def provide_list_items_use_case(
        self,
        storage: CompetencyMatrixStorage,
    ) -> AbstractListItemsUseCase:
        return ListItemsUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    async def provide_list_sheets_use_case(
        self,
        storage: CompetencyMatrixStorage,
    ) -> AbstractListSheetsUseCase:
        return ListSheetsUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    async def provide_get_item_use_case(
        self,
        storage: CompetencyMatrixStorage,
    ) -> AbstractGetItemUseCase:
        return GetItemUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    async def provide_create_item_use_case(
        self,
        storage: CompetencyMatrixStorage,
    ) -> AbstractUpsertItemUseCase:
        return UpsertItemUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    async def provide_delete_item_use_case(
        self,
        storage: CompetencyMatrixStorage,
    ) -> AbstractDeleteItemUseCase:
        return DeleteItemUseCase(storage=storage)
