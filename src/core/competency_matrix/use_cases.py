from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItems,
    Sheets,
)
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.use_cases import UseCase


class AbstractListSheetsUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self) -> Sheets:
        raise NotImplementedError


class AbstractListItemsUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(
        self,
        *,
        sheet_name: str,
        only_published: bool,
    ) -> CompetencyMatrixItems:
        raise NotImplementedError


class AbstractGetItemUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(
        self,
        *,
        item_id: int,
        only_published: bool,
    ) -> CompetencyMatrixItem:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class ListSheetsUseCase(AbstractListSheetsUseCase):
    storage: CompetencyMatrixStorage

    async def execute(self) -> Sheets:
        sheets = await self.storage.list_sheets()
        return Sheets(values=sheets)


@dataclass(kw_only=True, slots=True, frozen=True)
class ListItemsUseCase(AbstractListItemsUseCase):
    storage: CompetencyMatrixStorage

    async def execute(
        self,
        *,
        sheet_name: str,
        only_published: bool,
    ) -> CompetencyMatrixItems:
        items = await self.storage.list_competency_matrix_items(sheet_name=sheet_name)
        matrix = CompetencyMatrixItems(values=items)
        return matrix.only_available() if only_published else matrix


@dataclass(kw_only=True, slots=True, frozen=True)
class GetItemUseCase(AbstractGetItemUseCase):
    storage: CompetencyMatrixStorage

    async def execute(
        self,
        *,
        item_id: int,
        only_published: bool,
    ) -> CompetencyMatrixItem:
        item = await self.storage.get_competency_matrix_item(item_id=item_id)
        if only_published and not item.is_available():
            raise CompetencyMatrixItemNotFoundError
        return item
