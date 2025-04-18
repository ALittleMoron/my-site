from dataclasses import dataclass

from core.competency_matrix.enums import StatusEnum
from core.schemas import ValuedDataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Sheets(ValuedDataclass[str]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class Subsections(ValuedDataclass[str]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class ExternalResource:
    id: int
    name: str
    url: str
    context: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class ExternalResources(ValuedDataclass[ExternalResource]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItem:
    id: int
    question: str
    status: StatusEnum
    answer: str
    interview_expected_answer: str
    sheet: str
    grade: str
    section: str
    subsection: str
    resources: ExternalResources

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
