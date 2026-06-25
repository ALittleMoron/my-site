from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from math import ceil

from core.competency_matrix.enums import (
    CompetencyMatrixWorkspaceSortEnum,
    GradeEnum,
    InterviewFrequencyEnum,
)
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.schemas import ValuedDataclass
from core.types import IntId, SearchName


class CompetencyMatrixMissingFieldEnum(StrEnum):
    SLUG = "slug"
    SHEET_KEY = "sheetKey"
    GRADE = "grade"
    QUESTION_RU = "questionRu"
    QUESTION_EN = "questionEn"
    ANSWER_RU = "answerRu"
    ANSWER_EN = "answerEn"
    INTERVIEW_EXPECTED_ANSWER_RU = "interviewExpectedAnswerRu"
    INTERVIEW_EXPECTED_ANSWER_EN = "interviewExpectedAnswerEn"
    SHEET_RU = "sheetRu"
    SHEET_EN = "sheetEn"
    SECTION_RU = "sectionRu"
    SECTION_EN = "sectionEn"
    SUBSECTION_RU = "subsectionRu"
    SUBSECTION_EN = "subsectionEn"


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
class QueuedCompetencyMatrixQuestionsCreateParams:
    questions: list[QueuedCompetencyMatrixQuestionCreateParams]


@dataclass(frozen=True, slots=True, kw_only=True)
class QuestionQueueImportRules:
    supported_text_extensions: frozenset[str]
    supported_excel_extensions: frozenset[str]
    unsupported_legacy_excel_extensions: frozenset[str]
    supported_extensions_for_message: tuple[str, ...]
    question_headers: frozenset[str]
    question_headers_for_message: tuple[str, ...]
    csv_delimiters: str
    question_max_length: int


@dataclass(frozen=True, slots=True, kw_only=True)
class QuestionQueueImportFile:
    filename: str
    content: bytes


@dataclass(frozen=True, slots=True, kw_only=True)
class ParsedQuestionRow:
    row_number: int
    value: object


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
    interview_frequency: InterviewFrequencyEnum | None
    section_ru: str
    section_en: str
    subsection_ru: str
    subsection_en: str

    def is_available(self) -> bool:
        return (
            self.publish_status == PublishStatusEnum.PUBLISHED
            and not self.has_missing_publication_fields()
        )

    def has_missing_publication_fields(self) -> bool:
        return bool(self.missing_publication_fields())

    def missing_publication_fields(self) -> tuple[CompetencyMatrixMissingFieldEnum, ...]:
        checks = (
            (CompetencyMatrixMissingFieldEnum.SLUG, not self.slug.strip()),
            (CompetencyMatrixMissingFieldEnum.SHEET_KEY, not self.sheet_key.strip()),
            (CompetencyMatrixMissingFieldEnum.GRADE, self.grade is None),
            (CompetencyMatrixMissingFieldEnum.QUESTION_RU, not self.question_ru.strip()),
            (CompetencyMatrixMissingFieldEnum.QUESTION_EN, not self.question_en.strip()),
            (CompetencyMatrixMissingFieldEnum.ANSWER_RU, not self.answer_ru.strip()),
            (CompetencyMatrixMissingFieldEnum.ANSWER_EN, not self.answer_en.strip()),
            (
                CompetencyMatrixMissingFieldEnum.INTERVIEW_EXPECTED_ANSWER_RU,
                not self.interview_expected_answer_ru.strip(),
            ),
            (
                CompetencyMatrixMissingFieldEnum.INTERVIEW_EXPECTED_ANSWER_EN,
                not self.interview_expected_answer_en.strip(),
            ),
            (CompetencyMatrixMissingFieldEnum.SHEET_RU, not self.sheet_ru.strip()),
            (CompetencyMatrixMissingFieldEnum.SHEET_EN, not self.sheet_en.strip()),
            (CompetencyMatrixMissingFieldEnum.SECTION_RU, not self.section_ru.strip()),
            (CompetencyMatrixMissingFieldEnum.SECTION_EN, not self.section_en.strip()),
            (CompetencyMatrixMissingFieldEnum.SUBSECTION_RU, not self.subsection_ru.strip()),
            (CompetencyMatrixMissingFieldEnum.SUBSECTION_EN, not self.subsection_en.strip()),
        )
        return tuple(field for field, is_missing in checks if is_missing)

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
    published_at: datetime | None
    resources: AttachedExternalResources


@dataclass(slots=True, kw_only=True)
class CompetencyMatrixItemWriteParams(BaseCompetencyMatrixItem):
    grade: GradeEnum | None
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

    def to_item(
        self,
        *,
        resources: ExternalResources,
        published_at: datetime | None,
    ) -> CompetencyMatrixItem:
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
            published_at=published_at,
            answer_ru=self.answer_ru,
            answer_en=self.answer_en,
            interview_expected_answer_ru=self.interview_expected_answer_ru,
            interview_expected_answer_en=self.interview_expected_answer_en,
            sheet_key=self.sheet_key,
            sheet_ru=self.sheet_ru,
            sheet_en=self.sheet_en,
            grade=self.grade,
            interview_frequency=self.interview_frequency,
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
class CompetencyMatrixWorkspaceFilters:
    page: int
    page_size: int
    language: LanguageEnum
    sort: CompetencyMatrixWorkspaceSortEnum
    search_query: str | None = None
    sheet_keys: tuple[str, ...] = ()
    grades: tuple[GradeEnum, ...] = ()
    interview_frequencies: tuple[InterviewFrequencyEnum, ...] = ()
    sections: tuple[str, ...] = ()
    subsections: tuple[str, ...] = ()
    publish_statuses: tuple[PublishStatusEnum, ...] = ()
    published_from: date | None = None
    published_to: date | None = None
    has_missing_fields: bool | None = None

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixWorkspaceSummary:
    total: int
    draft: int
    missing_draft: int
    dangerous_published: int
    ready_published: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixWorkspaceItem:
    id: IntId
    slug: str
    question: str
    sheet_key: str
    sheet: str
    grade: GradeEnum | None
    interview_frequency: InterviewFrequencyEnum | None
    section: str
    subsection: str
    publish_status: PublishStatusEnum
    published_at: datetime | None
    missing_fields: tuple[CompetencyMatrixMissingFieldEnum, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixWorkspace(ValuedDataclass[CompetencyMatrixWorkspaceItem]):
    total_count: int
    total_pages: int
    summary: CompetencyMatrixWorkspaceSummary

    @classmethod
    def from_page(
        cls,
        *,
        values: list[CompetencyMatrixWorkspaceItem],
        total_count: int,
        page_size: int,
        summary: CompetencyMatrixWorkspaceSummary,
    ) -> CompetencyMatrixWorkspace:
        return cls(
            values=values,
            total_count=total_count,
            total_pages=ceil(total_count / page_size) if total_count > 0 else 0,
            summary=summary,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixFilterOption:
    key: str
    label: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixFilterSectionOption:
    label: str
    subsections: list[str]


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixFilterSheetOption(CompetencyMatrixFilterOption):
    sections: list[CompetencyMatrixFilterSectionOption]


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetencyMatrixFilterOptions:
    sheets: list[CompetencyMatrixFilterSheetOption]
    grades: list[GradeEnum]
    interview_frequencies: list[InterviewFrequencyEnum]
    sections: list[str]
    subsections: list[str]
    publish_statuses: list[PublishStatusEnum]


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
