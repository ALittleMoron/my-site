from dataclasses import dataclass

from app.core.competency_matrix.schemas import (
    CompetencyMatrixItems,
    FilledCompetencyMatrixItems,
    ListItemsParams,
    ListSubsectionsParams,
    Sheets,
    Subsections,
)
from app.core.use_cases import UseCase
from app.database.storages import CompetencyMatrixStorage


@dataclass(kw_only=True)
class ListSheetsUseCase(UseCase):
    storage: CompetencyMatrixStorage

    async def execute(self) -> Sheets:
        sheets = await self.storage.list_sheets()
        return Sheets(values=sheets)


@dataclass(kw_only=True)
class ListSubsectionsUseCase(UseCase):
    storage: CompetencyMatrixStorage

    async def execute(self, params: ListSubsectionsParams) -> Subsections:
        subsections = await self.storage.list_subsections(sheet_id=params.sheet_id)
        return Subsections(values=subsections)


@dataclass(kw_only=True)
class ListItemsUseCase(UseCase):
    storage: CompetencyMatrixStorage

    async def execute(self, params: ListItemsParams) -> FilledCompetencyMatrixItems:
        items = await self.storage.list_competency_matrix_items(sheet_id=params.sheet_id)
        return CompetencyMatrixItems(values=items).only_available()
