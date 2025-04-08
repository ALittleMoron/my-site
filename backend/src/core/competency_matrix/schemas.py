from dataclasses import dataclass
from datetime import datetime

from core.competency_matrix.enums import StatusEnum
from core.schemas import ValuedDataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Sheets(ValuedDataclass[str]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class Subsections(ValuedDataclass[str]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class Resource:
    id: int
    name: str
    url: str
    context: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class Resources(ValuedDataclass[Resource]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItem:
    id: int
    question: str
    status: StatusEnum
    status_changed: datetime
    answer: str
    interview_expected_answer: str
    sheet: str
    grade: str
    section: str
    subsection: str
    resources: Resources

    def is_available(self) -> bool:
        return all(
            [
                self.status == StatusEnum.PUBLISHED,
                self.sheet != "",
                self.grade != "",
                self.section != "",
                self.subsection != "",
            ],
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItems(ValuedDataclass[CompetencyMatrixItem]):
    def only_available(self) -> "CompetencyMatrixItems":
        return CompetencyMatrixItems(values=[item for item in self if item.is_available()])
