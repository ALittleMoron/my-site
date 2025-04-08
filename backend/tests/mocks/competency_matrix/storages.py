from dataclasses import field

from core.competency_matrix.schemas import CompetencyMatrixItem
from db.storages import CompetencyMatrixStorage


class MockCompetencyMatrixStorage(CompetencyMatrixStorage):
    sheets: list[str] = field(default_factory=list)
    items: list[CompetencyMatrixItem] = field(default_factory=list)

    async def list_sheets(self) -> list[str]:
        return self.sheets

    async def list_competency_matrix_items(self, sheet_name: str) -> list[CompetencyMatrixItem]:
        return [item for item in self.items if item.sheet.lower() == sheet_name.lower()]
