from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.competency_matrix.enums import GradeEnum
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.schemas import ValuedDataclass
from core.types import IntId, SearchName


@dataclass(frozen=True, slots=True, kw_only=True)
class Sheet:
    key: str
    name_ru: str
    name_en: str

    def localized_name(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.name_ru
        return self.name_en


@dataclass(frozen=True, slots=True, kw_only=True)
class Sheets(ValuedDataclass[Sheet]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class Subsections(ValuedDataclass[str]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class QueuedCompetencyMatrixQuestion:
    id: IntId
    question: str
    grade: GradeEnum | None
    sheet: str | None
    section: str | None
    subsection: str | None
    suggested_by_username: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class QueuedCompetencyMatrixQuestions(ValuedDataclass[QueuedCompetencyMatrixQuestion]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class QueuedCompetencyMatrixQuestionCreateParams:
    question: str


@dataclass(frozen=True, slots=True, kw_only=True)
class QuestionSuggestionLimitParams:
    client_identifier: str
    now: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class QuestionSuggestionCreateParams:
    question: QueuedCompetencyMatrixQuestionCreateParams
    limit: QuestionSuggestionLimitParams | None


@dataclass(frozen=True, slots=True, kw_only=True)
class QueuedCompetencyMatrixQuestionCreateItemParams:
    queued_question_id: IntId
    item: CompetencyMatrixItemCreateParams


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixResourceSearchParams:
    search_name: SearchName
    limit: int
    language: LanguageEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItemGetParams:
    item_id: IntId
    only_published: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItemBySlugGetParams:
    slug: str
    only_published: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItemPublishStatusSwitchParams:
    item_id: IntId
    publish_status: PublishStatusEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class QuestionSuggestionQuota:
    allowed: bool
    remaining: int


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseExternalResource:
    name_ru: str
    name_en: str
    url: str

    def localized_name(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.name_ru
        return self.name_en


@dataclass(frozen=True, slots=True, kw_only=True)
class ExternalResource(BaseExternalResource):
    id: IntId


@dataclass(frozen=True, slots=True, kw_only=True)
class AttachedExternalResource(ExternalResource):
    context_ru: str
    context_en: str

    def to_external_resource(self) -> ExternalResource:
        return ExternalResource(
            id=self.id,
            name_ru=self.name_ru,
            name_en=self.name_en,
            url=self.url,
        )

    def localized_context(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.context_ru
        return self.context_en


@dataclass(frozen=True, slots=True, kw_only=True)
class ExternalResources(ValuedDataclass[ExternalResource]):
    def all_resources_exists_by_ids(self, ids: set[IntId]) -> bool:
        return ids.difference({resource.id for resource in self.values}) == set()


@dataclass(frozen=True, slots=True, kw_only=True)
class AttachedExternalResources(ValuedDataclass[AttachedExternalResource]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class ExistingExternalResourceAttachment:
    resource_id: IntId
    context_ru: str
    context_en: str


@dataclass(frozen=True, slots=True, kw_only=True)
class NewExternalResourceAttachment:
    resource: ExternalResource
    context_ru: str
    context_en: str

    def to_attached_resource(self) -> AttachedExternalResource:
        return AttachedExternalResource(
            id=self.resource.id,
            name_ru=self.resource.name_ru,
            name_en=self.resource.name_en,
            url=self.resource.url,
            context_ru=self.context_ru,
            context_en=self.context_en,
        )


@dataclass(slots=True, kw_only=True)
class BaseCompetencyMatrixItem:
    id: IntId
    slug: str
    question_ru: str
    question_en: str
    publish_status: PublishStatusEnum
    answer_ru: str
    answer_en: str
    interview_expected_answer_ru: str
    interview_expected_answer_en: str
    sheet_key: str
    sheet_ru: str
    sheet_en: str
    grade: GradeEnum | None
    section_ru: str
    section_en: str
    subsection_ru: str
    subsection_en: str

    def is_available(self) -> bool:
        return all(
            [
                self.publish_status == PublishStatusEnum.PUBLISHED,
                self.slug != "",
                self.sheet_key != "",
                self.sheet_ru != "",
                self.sheet_en != "",
                self.grade is not None,
                self.section_ru != "",
                self.section_en != "",
                self.subsection_ru != "",
                self.subsection_en != "",
            ],
        )

    def localized_question(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.question_ru
        return self.question_en

    def localized_answer(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.answer_ru
        return self.answer_en

    def localized_interview_expected_answer(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.interview_expected_answer_ru
        return self.interview_expected_answer_en

    def localized_sheet(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.sheet_ru
        return self.sheet_en

    def localized_section(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.section_ru
        return self.section_en

    def localized_subsection(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.subsection_ru
        return self.subsection_en


@dataclass(slots=True, kw_only=True)
class CompetencyMatrixItem(BaseCompetencyMatrixItem):
    resources: AttachedExternalResources


@dataclass(slots=True, kw_only=True)
class CompetencyMatrixItemWriteParams(BaseCompetencyMatrixItem):
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
                name_ru=resource.name_ru,
                name_en=resource.name_en,
                url=resource.url,
                context_ru=attachment.context_ru,
                context_en=attachment.context_en,
            )
            for attachment in self.get_existing_resource_attachments()
            if (resource := resources_by_id.get(attachment.resource_id)) is not None
        ]
        attached_new_resources = [
            attachment.to_attached_resource() for attachment in self.get_new_resource_attachments()
        ]
        return CompetencyMatrixItem(
            id=self.id,
            slug=self.slug,
            question_ru=self.question_ru,
            question_en=self.question_en,
            publish_status=self.publish_status,
            answer_ru=self.answer_ru,
            answer_en=self.answer_en,
            interview_expected_answer_ru=self.interview_expected_answer_ru,
            interview_expected_answer_en=self.interview_expected_answer_en,
            sheet_key=self.sheet_key,
            sheet_ru=self.sheet_ru,
            sheet_en=self.sheet_en,
            grade=self.grade,
            section_ru=self.section_ru,
            section_en=self.section_en,
            subsection_ru=self.subsection_ru,
            subsection_en=self.subsection_en,
            resources=AttachedExternalResources(
                values=[*attached_existing_resources, *attached_new_resources],
            ),
        )


@dataclass(slots=True, kw_only=True)
class CompetencyMatrixItemCreateParams(CompetencyMatrixItemWriteParams): ...


@dataclass(slots=True, kw_only=True)
class CompetencyMatrixItemUpdateParams(CompetencyMatrixItemWriteParams): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItemFilters:
    sheet_key: str | None = None
    only_published: bool | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixItems(ValuedDataclass[CompetencyMatrixItem]):
    def only_available(self) -> CompetencyMatrixItems:
        return CompetencyMatrixItems(values=[item for item in self if item.is_available()])

    def to_published_for_seo(self) -> PublishedCompetencyMatrixItemsForSeo:
        return PublishedCompetencyMatrixItemsForSeo(
            values=[
                PublishedCompetencyMatrixItemForSeo(
                    slug=item.slug,
                    publish_status=item.publish_status,
                )
                for item in self
            ],
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishedCompetencyMatrixItemForSeo:
    slug: str
    publish_status: PublishStatusEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishedCompetencyMatrixItemsForSeo(
    ValuedDataclass[PublishedCompetencyMatrixItemForSeo],
): ...
