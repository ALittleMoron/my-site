from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItems,
    Sheets,
)
from core.use_cases import UseCase
from db.storages.competency_matrix import CompetencyMatrixStorage


class AbstractListSheetsUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self) -> Sheets:
        raise NotImplementedError


class AbstractListItemsUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self, sheet_name: str) -> CompetencyMatrixItems:
        raise NotImplementedError


class AbstractGetItemUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self, item_id: int) -> CompetencyMatrixItem:
        raise NotImplementedError


@dataclass(kw_only=True)
class ListSheetsUseCase(AbstractListSheetsUseCase):
    storage: CompetencyMatrixStorage

    async def execute(self) -> Sheets:
        sheets = await self.storage.list_sheets()
        return Sheets(values=sheets)


@dataclass(kw_only=True)
class ListItemsUseCase(AbstractListItemsUseCase):
    storage: CompetencyMatrixStorage

    async def execute(self, sheet_name: str) -> CompetencyMatrixItems:
        items = await self.storage.list_competency_matrix_items(sheet_name=sheet_name)
        return CompetencyMatrixItems(values=items).only_available()


@dataclass(kw_only=True)
class GetItemUseCase(AbstractGetItemUseCase):
    storage: CompetencyMatrixStorage

    async def execute(self, item_id: int) -> CompetencyMatrixItem:
        item = await self.storage.get_competency_matrix_item(item_id=item_id)
        if not item.is_available():
            raise CompetencyMatrixItemNotFoundError
        return item
