from collections.abc import Iterable
from itertools import groupby
from typing import Annotated, Self

from pydantic import Field, field_validator

from core.competency_matrix.enums import GradeEnum, InterviewFrequencyEnum
from core.competency_matrix.generators import ItemIdGenerator, ResourceIdGenerator
from core.competency_matrix.schemas import (
    AttachedExternalResource,
    CompetencyMatrixFilterOption,
    CompetencyMatrixFilterOptions,
    CompetencyMatrixFilterSectionOption,
    CompetencyMatrixFilterSheetOption,
    CompetencyMatrixItem,
    CompetencyMatrixItemCreateParams,
    CompetencyMatrixItems,
    CompetencyMatrixItemUpdateParams,
    CompetencyMatrixMissingFieldEnum,
    CompetencyMatrixWorkspace,
    CompetencyMatrixWorkspaceItem,
    CompetencyMatrixWorkspaceSummary,
    ExistingExternalResourceAttachment,
    ExternalResource,
    ExternalResources,
    NewExternalResourceAttachment,
    QuestionSuggestionCreateParams,
    QuestionSuggestionLimitParams,
    QueuedCompetencyMatrixQuestion,
    QueuedCompetencyMatrixQuestionCreateItemParams,
    QueuedCompetencyMatrixQuestionCreateParams,
    QueuedCompetencyMatrixQuestions,
    Sheet,
    Sheets,
)
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import IntId
from entrypoints.litestar.api.schemas import CamelCaseSchema


class ResourceTranslationSchema(CamelCaseSchema):
    name: Annotated[str, Field(title="Наименование", min_length=1, max_length=255)]


class ResourceTranslationsSchema(CamelCaseSchema):
    ru: Annotated[ResourceTranslationSchema, Field(title="Русский перевод")]
    en: Annotated[ResourceTranslationSchema, Field(title="Английский перевод")]


class QuestionSuggestionRequestSchema(CamelCaseSchema):
    question: Annotated[str, Field(title="Вопрос", min_length=1, max_length=255)]

    @field_validator("question", mode="after")
    @classmethod
    def normalize_question(cls, value: str) -> str:
        question = value.strip()
        if not question:
            msg = "question must not be blank"
            raise ValueError(msg)
        return question

    def to_schema(
        self,
        *,
        limit: QuestionSuggestionLimitParams | None,
    ) -> QuestionSuggestionCreateParams:
        return QuestionSuggestionCreateParams(
            question=QueuedCompetencyMatrixQuestionCreateParams(question=self.question),
            limit=limit,
        )


class QueuedQuestionResponseSchema(CamelCaseSchema):
    id: Annotated[int, Field(title="Идентификатор")]
    question: Annotated[str, Field(title="Вопрос")]
    grade: Annotated[GradeEnum | None, Field(title="Компетенция")]
    sheet: Annotated[str | None, Field(title="Лист")]
    section: Annotated[str | None, Field(title="Раздел")]
    subsection: Annotated[str | None, Field(title="Подраздел")]
    suggested_by_username: Annotated[str | None, Field(title="Кто предложил")]
    created_at: Annotated[str, Field(title="Дата создания")]

    @classmethod
    def from_domain_schema(cls, *, schema: QueuedCompetencyMatrixQuestion) -> Self:
        return cls(
            id=schema.id,
            question=schema.question,
            grade=schema.grade,
            sheet=schema.sheet,
            section=schema.section,
            subsection=schema.subsection,
            suggested_by_username=schema.suggested_by_username,
            created_at=schema.created_at.isoformat(),
        )


class QueuedQuestionsResponseSchema(CamelCaseSchema):
    questions: Annotated[list[QueuedQuestionResponseSchema], Field(title="Список")]

    @classmethod
    def from_domain_schema(cls, *, schema: QueuedCompetencyMatrixQuestions) -> Self:
        return cls(
            questions=[
                QueuedQuestionResponseSchema.from_domain_schema(schema=question)
                for question in schema
            ],
        )


class ResourceResponseSchema(CamelCaseSchema):
    id: Annotated[int, Field(title="Идентификатор")]
    name: Annotated[str, Field(title="Наименование")]
    url: Annotated[str, Field(title="Ссылка")]
    translations: Annotated[ResourceTranslationsSchema, Field(title="Переводы")]

    @classmethod
    def from_domain_schema(cls, *, schema: ExternalResource, language: LanguageEnum) -> Self:
        return cls(
            id=schema.id,
            name=schema.localized_name(language=language),
            url=schema.url,
            translations=ResourceTranslationsSchema(
                ru=ResourceTranslationSchema(name=schema.name_ru),
                en=ResourceTranslationSchema(name=schema.name_en),
            ),
        )


class ResourceRequestSchema(CamelCaseSchema):
    url: Annotated[str, Field(title="Ссылка", min_length=1, max_length=2048)]
    translations: Annotated[ResourceTranslationsSchema, Field(title="Переводы")]

    def to_schema(self, resource_id: IntId) -> ExternalResource:
        return ExternalResource(
            id=resource_id,
            name_ru=self.translations.ru.name,
            name_en=self.translations.en.name,
            url=self.url,
        )


class AttachmentContextTranslationSchema(CamelCaseSchema):
    context: Annotated[str, Field(title="Контекст")]


class AttachmentContextTranslationsSchema(CamelCaseSchema):
    ru: Annotated[AttachmentContextTranslationSchema, Field(title="Русский перевод")]
    en: Annotated[AttachmentContextTranslationSchema, Field(title="Английский перевод")]


class AttachedResourceTranslationSchema(CamelCaseSchema):
    name: Annotated[str, Field(title="Наименование")]
    context: Annotated[str, Field(title="Контекст")]


class AttachedResourceTranslationsSchema(CamelCaseSchema):
    ru: Annotated[AttachedResourceTranslationSchema, Field(title="Русский перевод")]
    en: Annotated[AttachedResourceTranslationSchema, Field(title="Английский перевод")]


class AttachedResourceResponseSchema(CamelCaseSchema):
    id: Annotated[int, Field(title="Идентификатор")]
    name: Annotated[str, Field(title="Наименование")]
    url: Annotated[str, Field(title="Ссылка")]
    context: Annotated[str, Field(title="Контекст")]
    translations: Annotated[AttachedResourceTranslationsSchema, Field(title="Переводы")]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        schema: AttachedExternalResource,
        language: LanguageEnum,
    ) -> Self:
        return cls(
            id=schema.id,
            name=schema.localized_name(language=language),
            url=schema.url,
            context=schema.localized_context(language=language),
            translations=AttachedResourceTranslationsSchema(
                ru=AttachedResourceTranslationSchema(
                    name=schema.name_ru,
                    context=schema.context_ru,
                ),
                en=AttachedResourceTranslationSchema(
                    name=schema.name_en,
                    context=schema.context_en,
                ),
            ),
        )


class ExistingResourceAttachmentRequestSchema(CamelCaseSchema):
    resource_id: Annotated[int, Field(title="Идентификатор")]
    translations: Annotated[AttachmentContextTranslationsSchema, Field(title="Переводы")]

    def to_schema(self) -> ExistingExternalResourceAttachment:
        return ExistingExternalResourceAttachment(
            resource_id=IntId(self.resource_id),
            context_ru=self.translations.ru.context,
            context_en=self.translations.en.context,
        )


class NewResourceAttachmentRequestSchema(CamelCaseSchema):
    resource: Annotated[
        ResourceRequestSchema,
        Field(title="Ресурс"),
    ]
    translations: Annotated[AttachmentContextTranslationsSchema, Field(title="Переводы")]

    def to_schema(self, resource_id: IntId) -> NewExternalResourceAttachment:
        return NewExternalResourceAttachment(
            resource=self.resource.to_schema(resource_id=resource_id),
            context_ru=self.translations.ru.context,
            context_en=self.translations.en.context,
        )


class CompetencyMatrixItemTranslationSchema(CamelCaseSchema):
    question: Annotated[str, Field(title="Вопрос", min_length=1, max_length=255)]
    answer: Annotated[str, Field(title="Ответ")]
    interview_expected_answer: Annotated[str, Field(title="Ожидаемый ответ")]
    sheet: Annotated[str, Field(title="Лист", max_length=255)]
    section: Annotated[str, Field(title="Раздел", max_length=255)]
    subsection: Annotated[str, Field(title="Подраздел", max_length=255)]


class CompetencyMatrixItemTranslationsSchema(CamelCaseSchema):
    ru: Annotated[CompetencyMatrixItemTranslationSchema, Field(title="Русский перевод")]
    en: Annotated[CompetencyMatrixItemTranslationSchema, Field(title="Английский перевод")]

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixItem) -> Self:
        return cls(
            ru=CompetencyMatrixItemTranslationSchema(
                question=schema.question_ru,
                answer=schema.answer_ru,
                interview_expected_answer=schema.interview_expected_answer_ru,
                sheet=schema.sheet_ru,
                section=schema.section_ru,
                subsection=schema.subsection_ru,
            ),
            en=CompetencyMatrixItemTranslationSchema(
                question=schema.question_en,
                answer=schema.answer_en,
                interview_expected_answer=schema.interview_expected_answer_en,
                sheet=schema.sheet_en,
                section=schema.section_en,
                subsection=schema.subsection_en,
            ),
        )


class CompetencyMatrixItemResponseSchema(CamelCaseSchema):
    id: Annotated[int, Field(title="Идентификатор")]
    slug: Annotated[str, Field(title="Slug")]
    question: Annotated[str, Field(title="Вопрос")]
    interview_frequency: Annotated[
        InterviewFrequencyEnum | None,
        Field(title="Частота вопроса на собеседованиях"),
    ]

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixItem, language: LanguageEnum) -> Self:
        return cls(
            id=schema.id,
            slug=schema.slug,
            question=schema.localized_question(language=language),
            interview_frequency=schema.interview_frequency,
        )


class CompetencyMatrixItemDetailResponseSchema(CompetencyMatrixItemResponseSchema):
    answer: Annotated[str, Field(title="Ответ")]
    interview_expected_answer: Annotated[str, Field(title="Ожидаемый ответ")]
    sheet_key: Annotated[str, Field(title="Ключ листа")]
    sheet: Annotated[str, Field(title="Лист")]
    grade: Annotated[GradeEnum | None, Field(title="Компетенция")]
    section: Annotated[str, Field(title="Раздел")]
    subsection: Annotated[str, Field(title="Подраздел")]
    publish_status: Annotated[PublishStatusEnum, Field(title="Статус публикации")]
    resources: Annotated[list[AttachedResourceResponseSchema], Field(title="Ресурсы")]
    translations: Annotated[CompetencyMatrixItemTranslationsSchema, Field(title="Переводы")]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        schema: CompetencyMatrixItem,
        language: LanguageEnum,
    ) -> Self:
        summary = CompetencyMatrixItemResponseSchema.from_domain_schema(
            schema=schema,
            language=language,
        )
        return cls(
            **summary.model_dump(),
            answer=schema.localized_answer(language=language),
            interview_expected_answer=schema.localized_interview_expected_answer(
                language=language,
            ),
            sheet_key=schema.sheet_key,
            sheet=schema.localized_sheet(language=language),
            grade=schema.grade,
            section=schema.localized_section(language=language),
            subsection=schema.localized_subsection(language=language),
            publish_status=schema.publish_status,
            resources=[
                AttachedResourceResponseSchema.from_domain_schema(
                    schema=resource,
                    language=language,
                )
                for resource in schema.resources
            ],
            translations=CompetencyMatrixItemTranslationsSchema.from_domain_schema(schema=schema),
        )


class CompetencyMatrixItemRequestSchema(CamelCaseSchema):
    slug: Annotated[str, Field(title="Slug", min_length=1, max_length=255)]
    sheet_key: Annotated[str, Field(title="Ключ листа", min_length=1, max_length=255)]
    grade: Annotated[GradeEnum | None, Field(title="Компетенция")]
    interview_frequency: Annotated[
        InterviewFrequencyEnum | None,
        Field(title="Частота вопроса на собеседованиях"),
    ]
    publish_status: Annotated[PublishStatusEnum, Field(title="Статус публикации")]
    translations: Annotated[CompetencyMatrixItemTranslationsSchema, Field(title="Переводы")]
    resources: Annotated[
        list[ExistingResourceAttachmentRequestSchema | NewResourceAttachmentRequestSchema],
        Field(title="Ресурсы"),
    ]

    def to_create_schema(
        self,
        item_id_generator: ItemIdGenerator,
        resource_id_generator: ResourceIdGenerator,
    ) -> CompetencyMatrixItemCreateParams:
        return CompetencyMatrixItemCreateParams(
            id=item_id_generator.get_next(),
            slug=self.slug,
            question_ru=self.translations.ru.question,
            question_en=self.translations.en.question,
            answer_ru=self.translations.ru.answer,
            answer_en=self.translations.en.answer,
            interview_expected_answer_ru=self.translations.ru.interview_expected_answer,
            interview_expected_answer_en=self.translations.en.interview_expected_answer,
            sheet_key=self.sheet_key,
            sheet_ru=self.translations.ru.sheet,
            sheet_en=self.translations.en.sheet,
            grade=self.grade,
            interview_frequency=self.interview_frequency,
            section_ru=self.translations.ru.section,
            section_en=self.translations.en.section,
            subsection_ru=self.translations.ru.subsection,
            subsection_en=self.translations.en.subsection,
            publish_status=self.publish_status,
            resources=self._to_resource_attachments(resource_id_generator=resource_id_generator),
        )

    def to_create_from_queue_schema(
        self,
        queued_question_id: IntId,
        item_id_generator: ItemIdGenerator,
        resource_id_generator: ResourceIdGenerator,
    ) -> QueuedCompetencyMatrixQuestionCreateItemParams:
        return QueuedCompetencyMatrixQuestionCreateItemParams(
            queued_question_id=queued_question_id,
            item=self.to_create_schema(
                item_id_generator=item_id_generator,
                resource_id_generator=resource_id_generator,
            ),
        )

    def to_update_schema(
        self,
        item_id: IntId,
        resource_id_generator: ResourceIdGenerator,
    ) -> CompetencyMatrixItemUpdateParams:
        return CompetencyMatrixItemUpdateParams(
            id=item_id,
            slug=self.slug,
            question_ru=self.translations.ru.question,
            question_en=self.translations.en.question,
            answer_ru=self.translations.ru.answer,
            answer_en=self.translations.en.answer,
            interview_expected_answer_ru=self.translations.ru.interview_expected_answer,
            interview_expected_answer_en=self.translations.en.interview_expected_answer,
            sheet_key=self.sheet_key,
            sheet_ru=self.translations.ru.sheet,
            sheet_en=self.translations.en.sheet,
            grade=self.grade,
            interview_frequency=self.interview_frequency,
            section_ru=self.translations.ru.section,
            section_en=self.translations.en.section,
            subsection_ru=self.translations.ru.subsection,
            subsection_en=self.translations.en.subsection,
            publish_status=self.publish_status,
            resources=self._to_resource_attachments(resource_id_generator=resource_id_generator),
        )

    def _to_resource_attachments(
        self,
        resource_id_generator: ResourceIdGenerator,
    ) -> list[ExistingExternalResourceAttachment | NewExternalResourceAttachment]:
        return [
            resource.to_schema()
            if isinstance(resource, ExistingResourceAttachmentRequestSchema)
            else resource.to_schema(resource_id=resource_id_generator.get_next())
            for resource in self.resources
        ]


class CompetencyMatrixGroupedGradesResponseSchema(CamelCaseSchema):
    grade: Annotated[GradeEnum | None, Field(title="Компетенция")]
    items: Annotated[list[CompetencyMatrixItemResponseSchema], Field(title="Список")]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        grade: GradeEnum | None,
        items: Iterable[CompetencyMatrixItem],
        language: LanguageEnum,
    ) -> Self:
        return cls(
            grade=grade,
            items=[
                CompetencyMatrixItemResponseSchema.from_domain_schema(
                    schema=item,
                    language=language,
                )
                for item in items
            ],
        )


class CompetencyMatrixGroupedSubsectionsResponseSchema(CamelCaseSchema):
    subsection: Annotated[str, Field(title="Подраздел")]
    grades: Annotated[list[CompetencyMatrixGroupedGradesResponseSchema], Field(title="Список")]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        subsection: str,
        items: Iterable[CompetencyMatrixItem],
        language: LanguageEnum,
    ) -> Self:
        return cls(
            subsection=subsection,
            grades=[
                CompetencyMatrixGroupedGradesResponseSchema.from_domain_schema(
                    grade=grade,
                    items=list(grade_items),
                    language=language,
                )
                for grade, grade_items in groupby(items, key=lambda item: item.grade)
            ],
        )


class CompetencyMatrixGroupedSectionsResponseSchema(CamelCaseSchema):
    section: Annotated[str, Field(title="Раздел")]
    subsections: Annotated[
        list[CompetencyMatrixGroupedSubsectionsResponseSchema],
        Field(title="Список"),
    ]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        section: str,
        items: Iterable[CompetencyMatrixItem],
        language: LanguageEnum,
    ) -> Self:
        return cls(
            section=section,
            subsections=[
                CompetencyMatrixGroupedSubsectionsResponseSchema.from_domain_schema(
                    subsection=subsection,
                    items=list(subsection_items),
                    language=language,
                )
                for subsection, subsection_items in groupby(
                    items,
                    key=lambda item: item.localized_subsection(language=language),
                )
            ],
        )


class CompetencyMatrixItemsListResponseSchema(CamelCaseSchema):
    sheet_key: Annotated[str, Field(title="Ключ листа")]
    sheet: Annotated[str, Field(title="Лист")]
    sections: Annotated[
        list[CompetencyMatrixGroupedSectionsResponseSchema],
        Field(title="Список"),
    ]

    @classmethod
    def empty(cls, *, sheet_key: str) -> Self:
        return cls(sheet_key=sheet_key, sheet="", sections=[])

    @classmethod
    def from_domain_schema(
        cls,
        *,
        sheet_key: str,
        schema: CompetencyMatrixItems,
        language: LanguageEnum,
    ) -> Self:
        items = sorted(
            [item for item in schema.values if item.sheet_key == sheet_key],
            key=lambda item: (
                item.localized_section(language=language).lower(),
                item.localized_subsection(language=language).lower(),
                item.grade.value if item.grade is not None else "",
                item.id,
            ),
        )
        if not items:
            return cls.empty(sheet_key=sheet_key)
        sections = [
            CompetencyMatrixGroupedSectionsResponseSchema.from_domain_schema(
                section=section,
                items=list(section_items),
                language=language,
            )
            for section, section_items in groupby(
                items,
                key=lambda item: item.localized_section(language=language),
            )
        ]
        return cls(
            sheet_key=sheet_key,
            sheet=items[0].localized_sheet(language=language),
            sections=sections,
        )


class SheetResponseSchema(CamelCaseSchema):
    key: Annotated[str, Field(title="Ключ")]
    name: Annotated[str, Field(title="Название")]

    @classmethod
    def from_domain_schema(cls, *, schema: Sheet, language: LanguageEnum) -> Self:
        return cls(key=schema.key, name=schema.localized_name(language=language))


class CompetencyMatrixSheetsListResponseSchema(CamelCaseSchema):
    sheets: Annotated[list[SheetResponseSchema], Field(title="Список")]

    @classmethod
    def from_domain_schema(cls, *, schema: Sheets, language: LanguageEnum) -> Self:
        return cls(
            sheets=[
                SheetResponseSchema.from_domain_schema(schema=sheet, language=language)
                for sheet in schema
            ],
        )


class CompetencyMatrixResourcesResponseSchema(CamelCaseSchema):
    resources: Annotated[list[ResourceResponseSchema], Field(title="Ресурсы")]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        schema: ExternalResources,
        language: LanguageEnum,
    ) -> Self:
        return cls(
            resources=[
                ResourceResponseSchema.from_domain_schema(schema=resource, language=language)
                for resource in schema
            ],
        )


class CompetencyMatrixWorkspaceSummaryResponseSchema(CamelCaseSchema):
    total: Annotated[int, Field(title="Всего")]
    draft: Annotated[int, Field(title="Черновиков")]
    missing_draft: Annotated[int, Field(title="Черновиков с пропусками")]
    dangerous_published: Annotated[int, Field(title="Опубликованных с пропусками")]
    ready_published: Annotated[int, Field(title="Готовых опубликованных")]

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixWorkspaceSummary) -> Self:
        return cls(
            total=schema.total,
            draft=schema.draft,
            missing_draft=schema.missing_draft,
            dangerous_published=schema.dangerous_published,
            ready_published=schema.ready_published,
        )


class CompetencyMatrixWorkspaceItemResponseSchema(CamelCaseSchema):
    id: Annotated[int, Field(title="Идентификатор")]
    slug: Annotated[str, Field(title="Slug")]
    question: Annotated[str, Field(title="Вопрос")]
    sheet_key: Annotated[str, Field(title="Ключ листа")]
    sheet: Annotated[str, Field(title="Лист")]
    grade: Annotated[GradeEnum | None, Field(title="Компетенция")]
    interview_frequency: Annotated[
        InterviewFrequencyEnum | None,
        Field(title="Частота вопроса на собеседованиях"),
    ]
    section: Annotated[str, Field(title="Раздел")]
    subsection: Annotated[str, Field(title="Подраздел")]
    publish_status: Annotated[PublishStatusEnum, Field(title="Статус публикации")]
    published_at: Annotated[str | None, Field(title="Дата публикации")]
    missing_fields: Annotated[
        list[CompetencyMatrixMissingFieldEnum],
        Field(title="Незаполненные поля"),
    ]

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixWorkspaceItem) -> Self:
        return cls(
            id=schema.id,
            slug=schema.slug,
            question=schema.question,
            sheet_key=schema.sheet_key,
            sheet=schema.sheet,
            grade=schema.grade,
            interview_frequency=schema.interview_frequency,
            section=schema.section,
            subsection=schema.subsection,
            publish_status=schema.publish_status,
            published_at=schema.published_at.isoformat()
            if schema.published_at is not None
            else None,
            missing_fields=list(schema.missing_fields),
        )


class CompetencyMatrixWorkspaceResponseSchema(CamelCaseSchema):
    total_count: Annotated[int, Field(title="Количество вопросов")]
    total_pages: Annotated[int, Field(title="Количество страниц")]
    summary: Annotated[CompetencyMatrixWorkspaceSummaryResponseSchema, Field(title="Сводка")]
    items: Annotated[list[CompetencyMatrixWorkspaceItemResponseSchema], Field(title="Вопросы")]

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixWorkspace) -> Self:
        return cls(
            total_count=schema.total_count,
            total_pages=schema.total_pages,
            summary=CompetencyMatrixWorkspaceSummaryResponseSchema.from_domain_schema(
                schema=schema.summary,
            ),
            items=[
                CompetencyMatrixWorkspaceItemResponseSchema.from_domain_schema(schema=item)
                for item in schema
            ],
        )


class CompetencyMatrixFilterOptionResponseSchema(CamelCaseSchema):
    key: Annotated[str, Field(title="Ключ")]
    label: Annotated[str, Field(title="Подпись")]

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixFilterOption) -> Self:
        return cls(key=schema.key, label=schema.label)


class CompetencyMatrixFilterSectionOptionResponseSchema(CamelCaseSchema):
    label: Annotated[str, Field(title="Раздел")]
    subsections: Annotated[list[str], Field(title="Подразделы")]

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixFilterSectionOption) -> Self:
        return cls(label=schema.label, subsections=schema.subsections)


class CompetencyMatrixFilterSheetOptionResponseSchema(CamelCaseSchema):
    key: Annotated[str, Field(title="Ключ")]
    label: Annotated[str, Field(title="Подпись")]
    sections: Annotated[
        list[CompetencyMatrixFilterSectionOptionResponseSchema],
        Field(title="Разделы"),
    ]

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixFilterSheetOption) -> Self:
        return cls(
            key=schema.key,
            label=schema.label,
            sections=[
                CompetencyMatrixFilterSectionOptionResponseSchema.from_domain_schema(
                    schema=section,
                )
                for section in schema.sections
            ],
        )


class CompetencyMatrixFilterOptionsResponseSchema(CamelCaseSchema):
    sheets: Annotated[list[CompetencyMatrixFilterSheetOptionResponseSchema], Field(title="Листы")]
    grades: Annotated[list[GradeEnum], Field(title="Компетенции")]
    interview_frequencies: Annotated[
        list[InterviewFrequencyEnum],
        Field(title="Частоты вопросов на собеседованиях"),
    ]
    sections: Annotated[list[str], Field(title="Разделы")]
    subsections: Annotated[list[str], Field(title="Подразделы")]
    publish_statuses: Annotated[list[PublishStatusEnum], Field(title="Статусы публикации")]

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixFilterOptions) -> Self:
        return cls(
            sheets=[
                CompetencyMatrixFilterSheetOptionResponseSchema.from_domain_schema(schema=sheet)
                for sheet in schema.sheets
            ],
            grades=schema.grades,
            interview_frequencies=schema.interview_frequencies,
            sections=schema.sections,
            subsections=schema.subsections,
            publish_statuses=schema.publish_statuses,
        )
