from dataclasses import field

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.schemas import CompetencyMatrixItem
from db.storages.competency_matrix import CompetencyMatrixStorage


class MockCompetencyMatrixStorage(CompetencyMatrixStorage):
    sheets: list[str] = field(default_factory=list)
    items: list[CompetencyMatrixItem] = field(default_factory=list)

    async def list_sheets(self) -> list[str]:
        return self.sheets

    async def list_competency_matrix_items(self, sheet_name: str) -> list[CompetencyMatrixItem]:
        return [item for item in self.items if item.sheet.lower() == sheet_name.lower()]

    async def get_competency_matrix_item(self, item_id: int) -> CompetencyMatrixItem:
        try:
            return next(filter(lambda item: item.id == item_id, self.items))
        except StopIteration:
            raise CompetencyMatrixItemNotFoundError
