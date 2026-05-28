from dataclasses import dataclass

from core.competency_matrix.enums import GradeEnum
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


@dataclass(frozen=True, slots=True, kw_only=True)
class ExternalResource(BaseExternalResource):
    id: IntId


@dataclass(frozen=True, slots=True, kw_only=True)
class AttachedExternalResource(ExternalResource):
    context: str

    def to_external_resource(self) -> ExternalResource:
        return ExternalResource(id=self.id, name=self.name, url=self.url)


@dataclass(frozen=True, slots=True, kw_only=True)
class ExternalResources(ValuedDataclass[ExternalResource]):
    def all_resources_exists_by_ids(self, ids: set[IntId]) -> bool:
        return ids.difference({resource.id for resource in self.values}) == set()


@dataclass(frozen=True, slots=True, kw_only=True)
class AttachedExternalResources(ValuedDataclass[AttachedExternalResource]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class ExistingExternalResourceAttachment:
    resource_id: IntId
    context: str


@dataclass(frozen=True, slots=True, kw_only=True)
class NewExternalResourceAttachment:
    resource: ExternalResource
    context: str

    def to_attached_resource(self) -> AttachedExternalResource:
        return AttachedExternalResource(
            id=self.resource.id,
            name=self.resource.name,
            url=self.resource.url,
            context=self.context,
        )


@dataclass(slots=True, kw_only=True)
class BaseCompetencyMatrixItem:
    id: IntId
    question: str
    publish_status: PublishStatusEnum
    answer: str
    interview_expected_answer: str
    sheet: str
    grade: GradeEnum | None
    section: str
    subsection: str

    def is_available(self) -> bool:
        return all(
            [
                self.publish_status == PublishStatusEnum.PUBLISHED,
                self.sheet != "",
                self.grade is not None,
                self.section != "",
                self.subsection != "",
            ],
        )


@dataclass(slots=True, kw_only=True)
class CompetencyMatrixItem(BaseCompetencyMatrixItem):
    resources: AttachedExternalResources

    def set_publish_status(self, status: PublishStatusEnum) -> None:
        self.publish_status = status


@dataclass(slots=True, kw_only=True)
class CompetencyMatrixItemUpsertParams(BaseCompetencyMatrixItem):
    grade: GradeEnum
    resources: list[ExistingExternalResourceAttachment | NewExternalResourceAttachment]

    def get_new_resource_attachments(self) -> list[NewExternalResourceAttachment]:
        return [
            attachment
            for attachment in self.resources
            if isinstance(attachment, NewExternalResourceAttachment)
        ]

    def get_existing_resource_attachments(self) -> list[ExistingExternalResourceAttachment]:
        return [
            attachment
            for attachment in self.resources
            if isinstance(attachment, ExistingExternalResourceAttachment)
        ]

    def get_resource_ids_to_assign(self) -> list[IntId]:
        return [
            attachment.resource_id
            for attachment in self.resources
            if isinstance(attachment, ExistingExternalResourceAttachment)
        ]

    def to_item(self, resources: ExternalResources) -> CompetencyMatrixItem:
        resources_by_id = {resource.id: resource for resource in resources}
        attached_existing_resources = [
            AttachedExternalResource(
                id=resource.id,
                name=resource.name,
                url=resource.url,
                context=attachment.context,
            )
            for attachment in self.get_existing_resource_attachments()
            if (resource := resources_by_id.get(attachment.resource_id)) is not None
        ]
        attached_new_resources = [
            attachment.to_attached_resource() for attachment in self.get_new_resource_attachments()
        ]
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
            resources=AttachedExternalResources(
                values=[*attached_existing_resources, *attached_new_resources],
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItems(ValuedDataclass[CompetencyMatrixItem]):
    def only_available(self) -> CompetencyMatrixItems:
        return CompetencyMatrixItems(values=[item for item in self if item.is_available()])
