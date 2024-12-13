from dataclasses import dataclass
from datetime import datetime
from typing import cast

from app.core.competency_matrix.enums import StatusEnum
from app.core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from app.core.schemas import ValuedDataclass


@dataclass(kw_only=True)
class ListItemsParams:
    sheet_id: int


@dataclass(kw_only=True)
class ListSubsectionsParams:
    sheet_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Sheet:
    id: int
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Sheets(ValuedDataclass[Sheet]): ...


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
class Subsections(ValuedDataclass[Subsection]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class Grade:
    id: int
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Resource:
    id: int
    name: str
    url: str
    context: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class Resources(ValuedDataclass[Resource]): ...


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

    def is_short_available(self) -> bool:
        return all(
            [
                self.grade_id is not None,
                self.subsection_id is not None,
                self.status == StatusEnum.PUBLISHED,
            ],
        )


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

    def is_full_available(self) -> bool:
        return all([self.is_short_available(), self.grade is not None, self.subsection is not None])

    def to_full_filled(self) -> "FullFilledCompetencyMatrixItem":
        if not self.is_full_available():
            raise CompetencyMatrixItemNotFoundError
        return FullFilledCompetencyMatrixItem(
            id=self.id,
            question=self.question,
            answer=self.answer,
            interview_expected_answer=self.interview_expected_answer,
            status=self.status,
            status_changed=self.status_changed,
            grade_id=cast(int, self.grade_id),
            grade=cast(Grade, self.grade),
            subsection_id=cast(int, self.subsection_id),
            subsection=cast(Subsection, self.subsection),
            resources=self.resources,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class FullFilledCompetencyMatrixItem(ShortFilledCompetencyMatrixItem):
    answer: str
    interview_expected_answer: str
    grade: Grade
    subsection: Subsection
    resources: Resources


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItems(ValuedDataclass[ShortCompetencyMatrixItem]):
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
                for item in self
                if item.is_short_available()
            ],
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class FilledCompetencyMatrixItems(ValuedDataclass[ShortFilledCompetencyMatrixItem]): ...
