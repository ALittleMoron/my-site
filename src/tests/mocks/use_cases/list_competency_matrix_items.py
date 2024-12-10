from dataclasses import dataclass, field

from app.core.competency_matrix.schemas import (
    FilledCompetencyMatrixItems,
    ListCompetencyMatrixItemsParams,
    ShortFilledCompetencyMatrixItem,
)
from app.core.use_cases import UseCase


@dataclass
class MockListCompetencyMatrixItems(UseCase):
    items: list[ShortFilledCompetencyMatrixItem] = field(default_factory=list)
    params: ListCompetencyMatrixItemsParams | None | object = field(
        default_factory=lambda: object(),
    )

    async def execute(self, params: ListCompetencyMatrixItemsParams) -> FilledCompetencyMatrixItems:
        self.params = params
        return FilledCompetencyMatrixItems(values=self.items)
