from collections import defaultdict
from dataclasses import dataclass, field

from app.core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from app.core.competency_matrix.schemas import (
    FullCompetencyMatrixItem,
    Grade,
    Resource,
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
    resources: dict[int, list[Resource]] = field(default_factory=lambda: defaultdict(list))
    short_competency_matrix_items: dict[int, ShortCompetencyMatrixItem] = field(
        default_factory=dict,
    )
    full_competency_matrix_items: dict[int, FullCompetencyMatrixItem] = field(default_factory=dict)

    async def get_competency_matrix_item(self, item_id: int) -> FullCompetencyMatrixItem:
        try:
            return self.full_competency_matrix_items[item_id]
        except KeyError as exc:
            raise CompetencyMatrixItemNotFoundError from exc

    async def list_competency_matrix_items(
        self,
        sheet_id: int,
    ) -> list[ShortCompetencyMatrixItem]:
        return list(
            filter(
                lambda item: (
                    item.subsection_id is not None
                    and item.subsection_id in self.subsections
                    and self.subsections[item.subsection_id].section.sheet.id == sheet_id
                ),
                self.short_competency_matrix_items.values(),
            ),
        )

    async def list_sheets(self) -> list[Sheet]:
        return list(self.sheets.values())

    async def list_subsections(
        self,
        sheet_id: int,
    ) -> list[Subsection]:
        return list(
            filter(lambda item: item.section.sheet.id == sheet_id, self.subsections.values()),
        )
