from dataclasses import dataclass

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItems,
    Sheets,
)
from core.use_cases import UseCase
from db.storages import CompetencyMatrixStorage


@dataclass(kw_only=True)
class ListSheetsUseCase(UseCase):
    storage: CompetencyMatrixStorage

    async def execute(self) -> Sheets:
        sheets = await self.storage.list_sheets()
        return Sheets(values=sheets)


@dataclass(kw_only=True)
class ListItemsUseCase(UseCase):
    storage: CompetencyMatrixStorage

    async def execute(self, sheet_name: str) -> CompetencyMatrixItems:
        items = await self.storage.list_competency_matrix_items(sheet_name=sheet_name)
        return CompetencyMatrixItems(values=items).only_available()


@dataclass(kw_only=True)
class GetItemUseCase(UseCase):
    storage: CompetencyMatrixStorage

    async def execute(self, item_id: int) -> CompetencyMatrixItem:
        item = await self.storage.get_competency_matrix_item(item_id=item_id)
        if not item.is_available():
            raise CompetencyMatrixItemNotFoundError
        return item
