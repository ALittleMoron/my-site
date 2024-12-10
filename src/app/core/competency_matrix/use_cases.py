from dataclasses import dataclass

from app.core.competency_matrix.schemas import CompetencyMatrixItems, FilledCompetencyMatrixItems
from app.core.use_cases import UseCase
from app.database.storages import CompetencyMatrixStorage


@dataclass
class ListCompetencyMatrixItemsUseCase(UseCase):
    storage: CompetencyMatrixStorage

    async def execute(self, sheet_id: int | None = None) -> FilledCompetencyMatrixItems:
        items = await self.storage.list_competency_matrix_items(sheet_id=sheet_id)
        return CompetencyMatrixItems(values=items).only_available()
