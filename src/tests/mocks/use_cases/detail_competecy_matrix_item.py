from dataclasses import dataclass

from app.core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from app.core.competency_matrix.schemas import (
    FullFilledCompetencyMatrixItem,
)
from app.core.use_cases import UseCase


@dataclass
class MockGetItemUseCase(UseCase):
    item: FullFilledCompetencyMatrixItem | None = None
    raise_exception: Exception | None = None
    item_id: int | None = None

    async def execute(self, item_id: int) -> FullFilledCompetencyMatrixItem:
        self.item_id = item_id
        if self.raise_exception is not None:
            raise self.raise_exception
        if self.item is None:
            raise CompetencyMatrixItemNotFoundError
        return self.item
