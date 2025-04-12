from dataclasses import dataclass, field

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItems,
    Sheets,
)
from core.use_cases import UseCase


@dataclass(kw_only=True)
class MockListSheetsUseCase(UseCase):
    sheets: list[str] | None = field(default_factory=list)

    async def execute(self) -> Sheets:
        return Sheets(values=self.sheets or [])


@dataclass(kw_only=True)
class MockListItemsUseCase(UseCase):
    items: list[CompetencyMatrixItem] = field(default_factory=list)

    async def execute(self, sheet_name: str) -> CompetencyMatrixItems:
        return CompetencyMatrixItems(
            values=[item for item in self.items if item.sheet == sheet_name],
        )


@dataclass(kw_only=True)
class MockGetItemUseCase(UseCase):
    item_id: int | None = None
    item: CompetencyMatrixItem | None = None

    async def execute(self, item_id: int) -> CompetencyMatrixItem:
        self.item_id = item_id
        if self.item is None:
            raise CompetencyMatrixItemNotFoundError
        return self.item
