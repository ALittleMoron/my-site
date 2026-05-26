from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.competency_matrix.generators import ItemIdGenerator, ResourceIdGenerator
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import (
    AbstractCompetencyMatrixUseCase,
    CompetencyMatrixUseCase,
)
from infra.postgresql.storages.competency_matrix import CompetencyMatrixDatabaseStorage


class CompetencyMatrixProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_item_id_generator(self) -> ItemIdGenerator:
        return ItemIdGenerator()

    @provide(scope=Scope.APP)
    async def provide_resource_id_generator(self) -> ResourceIdGenerator:
        return ResourceIdGenerator()

    @provide(scope=Scope.REQUEST)
    async def provide_competency_matrix_storage(
        self,
        session: AsyncSession,
    ) -> CompetencyMatrixStorage:
        return CompetencyMatrixDatabaseStorage(session=session)

    @provide(scope=Scope.REQUEST)
    async def provide_competency_matrix_use_case(
        self,
        storage: CompetencyMatrixStorage,
    ) -> AbstractCompetencyMatrixUseCase:
        return CompetencyMatrixUseCase(storage=storage)
