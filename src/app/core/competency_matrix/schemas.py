from dataclasses import dataclass
from datetime import datetime

from app.core.competency_matrix.enums import StatusEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class Sheet:
    id: int
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Section:
    id: int
    name: str
    sheet: Sheet


@dataclass(frozen=True, slots=True, kw_only=True)
class Subsection:
    id: int
    name: str
    section: Section


@dataclass(frozen=True, slots=True, kw_only=True)
class Grade:
    id: int
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Resource:
    name: str
    url: str
    context: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class Resources:
    values: list[Resource]


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseCompetencyMatrixItem:
    id: int
    question: str
    status: StatusEnum
    status_changed: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class ShortCompetencyMatrixItem(BaseCompetencyMatrixItem):
    grade_id: int | None
    subsection_id: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ShortFilledCompetencyMatrixItem(BaseCompetencyMatrixItem):
    grade_id: int
    subsection_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class FullCompetencyMatrixItem(ShortCompetencyMatrixItem):
    answer: str
    interview_expected_answer: str
    grade: Grade | None
    subsection: Subsection | None
    resources: Resources


@dataclass(frozen=True, slots=True, kw_only=True)
class FullFilledCompetencyMatrixItem(ShortFilledCompetencyMatrixItem):
    answer: str
    interview_expected_answer: str
    grade: Grade
    subsection: Subsection
    resources: Resources


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItems:
    values: list[ShortCompetencyMatrixItem]

    def only_available(self) -> "FilledCompetencyMatrixItems":
        return FilledCompetencyMatrixItems(
            values=[
                ShortFilledCompetencyMatrixItem(
                    id=item.id,
                    question=item.question,
                    status=item.status,
                    status_changed=item.status_changed,
                    grade_id=item.grade_id,
                    subsection_id=item.subsection_id,
                )
                for item in self.values
                if item.grade_id is not None
                and item.subsection_id is not None
                and item.status == StatusEnum.PUBLISHED
            ],
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class FilledCompetencyMatrixItems:
    values: list[ShortFilledCompetencyMatrixItem]
