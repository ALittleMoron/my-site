import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from dateutil.parser import parse

from app.core.competency_matrix.enums import StatusEnum
from app.core.competency_matrix.schemas import (
    FullCompetencyMatrixItem,
    FullFilledCompetencyMatrixItem,
    Grade,
    Resource,
    Resources,
    Section,
    Sheet,
    ShortCompetencyMatrixItem,
    ShortFilledCompetencyMatrixItem,
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
            return self.context.current_datetime  # type: ignore[no-any-return]
        return parse(dt)  # type: ignore[no-any-return]

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

    def parse_grades(self) -> list[Grade]:
        return [
            Grade(
                id=row['grade.id'],
                name=row['grade.name'],
            )
            for row in self.context.table
        ]

    def parse_full_filled_competency_matrix_item(self) -> FullFilledCompetencyMatrixItem:
        data = dict(self.context.table)
        return FullFilledCompetencyMatrixItem(
            id=int(data['id']),
            question=data['question'],
            answer=data['answer'],
            interview_expected_answer=data['interview_expected_answer'],
            status=StatusEnum(data.get('status') or 'published'),
            status_changed=self.parse_datetime(data.get('status_changed')),
            grade_id=int(data['grade.id']),
            grade=Grade(
                id=int(data['grade.id']),
                name=data['grade.name'],
            ),
            subsection_id=int(data['subsection.id']),
            subsection=Subsection(
                id=int(data['subsection.id']),
                name=data['subsection.name'],
                section=Section(
                    id=int(data['section.id']),
                    name=data['section.name'],
                    sheet=Sheet(
                        id=int(data['sheet.id']),
                        name=data['sheet.name'],
                    ),
                ),
            ),
            resources=Resources(values=[]),
        )

    def parse_resources(self) -> list[Resource]:
        return [
            Resource(
                id=row['resource.id'],
                name=row['resource.name'],
                url=row.get('resource.url') or '',
                context=row.get('resource.context') or '',
            )
            for row in self.context.table
        ]

    def parse_full_filled_competency_matrix_items(self) -> list[FullFilledCompetencyMatrixItem]:
        return [
            FullFilledCompetencyMatrixItem(
                id=int(row['id']),
                question=row['question'],
                answer=row['answer'],
                interview_expected_answer=row['interview_expected_answer'],
                status=StatusEnum(row.get('status') or 'published'),
                status_changed=self.parse_datetime(row.get('status_changed')),
                grade_id=int(row['grade.id']),
                grade=Grade(
                    id=int(row['grade.id']),
                    name=row['grade.name'],
                ),
                subsection_id=int(row['subsection.id']),
                subsection=Subsection(
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
                ),
                resources=Resources(values=[]),
            )
            for row in self.context.table
        ]

    def parse_full_competency_matrix_items(self) -> list[FullCompetencyMatrixItem]:
        return [
            FullCompetencyMatrixItem(
                id=int(row['id']),
                question=row['question'],
                answer=row['answer'],
                interview_expected_answer=row['interview_expected_answer'],
                status=StatusEnum(row.get('status') or 'published'),
                status_changed=self.parse_datetime(row.get('status_changed')),
                grade_id=self.parse_int_or_none(row.get('grade.id')),
                grade=(
                    Grade(
                        id=int(row['grade.id']),
                        name=row['grade.name'],
                    )
                    if row.get('grade.id')
                    else None
                ),
                subsection_id=self.parse_int_or_none(row.get('subsection.id')),
                subsection=(
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
                    if row.get('subsection.id')
                    else None
                ),
                resources=Resources(values=[]),
            )
            for row in self.context.table
        ]
