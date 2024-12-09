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
    section: dict[int, Section] = field(default_factory=dict)
    subsection: dict[int, Subsection] = field(default_factory=dict)
    grade: dict[int, Grade] = field(default_factory=dict)
    short_competency_matrix_items: dict[int, ShortCompetencyMatrixItem] = field(
        default_factory=dict,
    )

    async def list_competency_matrix_items(self) -> list[ShortCompetencyMatrixItem]:
        return list(self.short_competency_matrix_items.values())
