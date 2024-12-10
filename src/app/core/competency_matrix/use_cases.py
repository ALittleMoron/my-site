from dataclasses import dataclass

from app.core.competency_matrix.schemas import (
    CompetencyMatrixItems,
    FilledCompetencyMatrixItems,
    ListCompetencyMatrixItemsParams,
)
from app.core.use_cases import UseCase
from app.database.storages import CompetencyMatrixStorage


@dataclass
class ListCompetencyMatrixItemsUseCase(UseCase):
    storage: CompetencyMatrixStorage

    async def execute(self, params: ListCompetencyMatrixItemsParams) -> FilledCompetencyMatrixItems:
        items = await self.storage.list_competency_matrix_items(sheet_id=params.sheet_id)
        return CompetencyMatrixItems(values=items).only_available()
