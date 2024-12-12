from dataclasses import dataclass, field

from app.core.competency_matrix.schemas import (
    FilledCompetencyMatrixItems,
    ListItemsParams,
    ShortFilledCompetencyMatrixItem,
)
from app.core.use_cases import UseCase


@dataclass
class MockListCompetencyMatrixItemsUseCase(UseCase):
    items: list[ShortFilledCompetencyMatrixItem] = field(default_factory=list)
    params: ListItemsParams | None | object = field(
        default_factory=lambda: object(),
    )

    async def execute(self, params: ListItemsParams) -> FilledCompetencyMatrixItems:
        self.params = params
        return FilledCompetencyMatrixItems(values=self.items)
