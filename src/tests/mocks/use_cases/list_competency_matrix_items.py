from dataclasses import dataclass, field

from app.core.competency_matrix.schemas import (
    FilledCompetencyMatrixItems,
    ShortFilledCompetencyMatrixItem,
)
from app.core.use_cases import UseCase


@dataclass
class MockListCompetencyMatrixItems(UseCase):
    items: list[ShortFilledCompetencyMatrixItem] = field(default_factory=list)

    async def execute(self) -> FilledCompetencyMatrixItems:
        return FilledCompetencyMatrixItems(values=self.items)
