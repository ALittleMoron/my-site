import datetime

from app.core.competency_matrix.enums import StatusEnum
from app.core.competency_matrix.schemas import (
    FilledCompetencyMatrixItems,
    ShortFilledCompetencyMatrixItem,
)


class FactoryHelper:
    @classmethod
    def short_filled_competency_matrix_item(
        cls,
        item_id: int,
        question: str,
        status: StatusEnum = StatusEnum.PUBLISHED,
        status_changed: datetime.datetime | None = None,
        grade_id: int = 1,
        subsection_id: int = 1,
    ) -> ShortFilledCompetencyMatrixItem:
        return ShortFilledCompetencyMatrixItem(
            id=item_id,
            question=question,
            status=status,
            status_changed=status_changed or datetime.datetime.now(tz=datetime.UTC),
            grade_id=grade_id,
            subsection_id=subsection_id,
        )

    @classmethod
    def filled_competency_matrix_items(
        cls,
        values: list[ShortFilledCompetencyMatrixItem] | None = None,
    ) -> FilledCompetencyMatrixItems:
        return FilledCompetencyMatrixItems(values=values or [])
