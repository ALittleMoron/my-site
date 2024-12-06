from dataclasses import dataclass

from app.core.competency_matrix.schemas import CompetencyMatrixItems, FilledCompetencyMatrixItems
from app.core.use_cases import UseCase
from app.database.storage import Storage


@dataclass
class ListCompetencyMatrixItemsUseCase(UseCase):
    storage: Storage

    async def execute(self) -> FilledCompetencyMatrixItems:
        items = await self.storage.list_competency_matrix_items()
        return CompetencyMatrixItems(values=items).only_available()
