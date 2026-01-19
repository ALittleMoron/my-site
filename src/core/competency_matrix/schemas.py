from dataclasses import dataclass

from core.enums import PublishStatusEnum
from core.schemas import ValuedDataclass
from core.types import IntId


@dataclass(frozen=True, slots=True, kw_only=True)
class Sheets(ValuedDataclass[str]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class Subsections(ValuedDataclass[str]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseExternalResource:
    name: str
    url: str
    context: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class ExternalResource(BaseExternalResource):
    id: IntId


@dataclass(frozen=True, slots=True, kw_only=True)
class ExternalResources(ValuedDataclass[ExternalResource]):
    def all_resources_exists_by_ids(self, ids: set[IntId]) -> bool:
        return ids.difference({resource.id for resource in self.values}) == set()


@dataclass(slots=True, kw_only=True)
class BaseCompetencyMatrixItem:
    id: IntId
    question: str
    publish_status: PublishStatusEnum
    answer: str
    interview_expected_answer: str
    sheet: str
    grade: str
    section: str
    subsection: str

    def is_available(self) -> bool:
        return all(
            [
                self.publish_status == PublishStatusEnum.PUBLISHED,
                self.sheet != "",
                self.grade != "",
                self.section != "",
                self.subsection != "",
            ],
        )


@dataclass(slots=True, kw_only=True)
class CompetencyMatrixItem(BaseCompetencyMatrixItem):
    resources: ExternalResources

    def set_publish_status(self, status: PublishStatusEnum) -> None:
        self.publish_status = status


@dataclass(slots=True, kw_only=True)
class CompetencyMatrixItemUpsertParams(BaseCompetencyMatrixItem):
    resources: list[IntId | ExternalResource]

    def get_external_resources(self) -> list[ExternalResource]:
        return [resource for resource in self.resources if isinstance(resource, ExternalResource)]

    def get_resource_ids_to_assign(self) -> list[IntId]:
        return [resource for resource in self.resources if isinstance(resource, int)]

    def to_item(self, resources: ExternalResources) -> "CompetencyMatrixItem":
        return CompetencyMatrixItem(
            id=self.id,
            question=self.question,
            publish_status=self.publish_status,
            answer=self.answer,
            interview_expected_answer=self.interview_expected_answer,
            sheet=self.sheet,
            grade=self.grade,
            section=self.section,
            subsection=self.subsection,
            resources=resources.extends(self.get_external_resources()),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItems(ValuedDataclass[CompetencyMatrixItem]):
    def only_available(self) -> "CompetencyMatrixItems":
        return CompetencyMatrixItems(values=[item for item in self if item.is_available()])
