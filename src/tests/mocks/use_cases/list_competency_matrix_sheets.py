from dataclasses import dataclass, field

from app.core.competency_matrix.schemas import Sheet, Sheets
from app.core.use_cases import UseCase


@dataclass
class MockListCompetencyMatrixSheetsUseCase(UseCase):
    sheets: list[Sheet] = field(default_factory=list)

    async def execute(self) -> Sheets:
        return Sheets(values=self.sheets)
