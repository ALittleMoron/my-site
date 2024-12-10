import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from dateutil.parser import parse

from app.core.competency_matrix.enums import StatusEnum
from app.core.competency_matrix.schemas import (
    ShortCompetencyMatrixItem,
    ShortFilledCompetencyMatrixItem,
    Sheet,
    Section,
    Subsection,
)

if TYPE_CHECKING:
    from tests.bdd.fixtures import Context


@dataclass(kw_only=True)
class BddHelper:
    context: "Context"

    @staticmethod
    def assert_equal(actual: Any, expected: Any, msg: str = "") -> None:
        assert actual == expected, f"{msg}\n{actual=}\n{expected=}"

    @staticmethod
    def parse_int_or_none(value: str | None) -> int | None:
        if not value:
            return None
        return int(value)

    def parse_datetime(self, dt: str | None) -> datetime.datetime:
        if not dt:
            return self.context.current_datetime
        return parse(dt)

    def parse_short_competency_matrix_items(self) -> list[ShortCompetencyMatrixItem]:
        return [
            ShortCompetencyMatrixItem(
                id=row['id'],
                question=row['question'],
                status=StatusEnum(row.get('status') or 'published'),
                status_changed=self.parse_datetime(row.get('status_changed')),
                grade_id=self.parse_int_or_none(row.get('grade.id')),
                subsection_id=self.parse_int_or_none(row.get('subsection.id')),
            )
            for row in self.context.table
        ]

    def parse_short_filled_competency_matrix_items(self) -> list[ShortFilledCompetencyMatrixItem]:
        return [
            ShortFilledCompetencyMatrixItem(
                id=row['id'],
                question=row['question'],
                status=StatusEnum(row.get('status') or 'published'),
                status_changed=self.parse_datetime(row.get('status_changed')),
                grade_id=self.parse_int_or_none(row['grade.id']),
                subsection_id=self.parse_int_or_none(row['subsection.id']),
            )
            for row in self.context.table
        ]

    def parse_sheets(self) -> list[Sheet]:
        return [
            Sheet(id=int(row['sheet.id']), name=row['sheet.name']) for row in self.context.table
        ]

    def parse_sections(self) -> list[Section]:
        return [
            Section(
                id=int(row['section.id']),
                name=row['section.name'],
                sheet=Sheet(
                    id=int(row['sheet.id']),
                    name=row['sheet.name'],
                ),
            )
            for row in self.context.table
        ]

    def parse_subsections(self):
        return [
            Subsection(
                id=int(row['subsection.id']),
                name=row['subsection.name'],
                section=Section(
                    id=int(row['section.id']),
                    name=row['section.name'],
                    sheet=Sheet(
                        id=int(row['sheet.id']),
                        name=row['sheet.name'],
                    ),
                ),
            )
            for row in self.context.table
        ]
