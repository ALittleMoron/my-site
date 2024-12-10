from dataclasses import dataclass, field

from app.core.competency_matrix.schemas import (
    Grade,
    Section,
    Sheet,
    ShortCompetencyMatrixItem,
    Subsection,
)
from app.database.storages import CompetencyMatrixStorage


@dataclass(kw_only=True)
class MockCompetencyMatrixStorage(CompetencyMatrixStorage):
    sheets: dict[int, Sheet] = field(default_factory=dict)
    sections: dict[int, Section] = field(default_factory=dict)
    subsections: dict[int, Subsection] = field(default_factory=dict)
    grades: dict[int, Grade] = field(default_factory=dict)
    short_competency_matrix_items: dict[int, ShortCompetencyMatrixItem] = field(
        default_factory=dict,
    )

    async def list_competency_matrix_items(
        self,
        sheet_id: int | None = None,
    ) -> list[ShortCompetencyMatrixItem]:
        if sheet_id is not None:
            return list(
                filter(
                    lambda item: (
                        item.subsection_id is not None
                        and item.subsection_id in self.subsections
                        and self.subsections[item.subsection_id].section.sheet.id == sheet_id
                    ),
                    self.short_competency_matrix_items.values(),
                )
            )
        return list(self.short_competency_matrix_items.values())
