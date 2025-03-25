from dataclasses import dataclass, field

from core.competency_matrix.schemas import Sheets
from core.use_cases import UseCase


@dataclass(kw_only=True)
class MockListSheetsUseCase(UseCase):
    sheets: list[str] | None = field(default_factory=list)

    async def execute(self) -> Sheets:
        return Sheets(values=self.sheets or [])