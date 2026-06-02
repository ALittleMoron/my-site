import re
import uuid
from datetime import date
from typing import Annotated, Self

from pydantic import Field

from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from core.notes.schemas import (
    Note,
    NoteAnalyticsDailyStats,
    NoteAnalyticsNoteStats,
    NoteAnalyticsStats,
    NoteAnalyticsTotals,
    NoteCreateParams,
    NotePublicStats,
    NotePublicStatsCollection,
    NoteReactionCounts,
    Notes,
    NoteTree,
    NoteTreeFolder,
    NoteTreeItem,
    NoteUpdateParams,
    Tag,
    TagCreateParams,
    Tags,
    TagUpdateParams,
)
from core.types import IntId
from entrypoints.litestar.api.schemas import CamelCaseSchema


class TagResponseSchema(CamelCaseSchema):
    id: Annotated[int, Field(title="Идентификатор")]
    name: Annotated[str, Field(title="Название")]
    slug: Annotated[str, Field(title="Slug")]
    deleted_at: Annotated[str | None, Field(title="Дата удаления")]
    translations: Annotated[TagTranslationsResponseSchema, Field(title="Переводы")]

    @classmethod
    def from_domain_schema(cls, *, schema: Tag, language: LanguageEnum) -> Self:
        return cls(
            id=schema.id,
            name=schema.localized_name(language=language),
            slug=schema.slug,
            deleted_at=schema.deleted_at.isoformat() if schema.deleted_at is not None else None,
            translations=TagTranslationsResponseSchema.from_domain_schema(schema=schema),
        )


class TagTranslationSchema(CamelCaseSchema):
    name: Annotated[str, Field(title="Название", min_length=1, max_length=255)]


class TagTranslationsSchema(CamelCaseSchema):
    ru: Annotated[TagTranslationSchema, Field(title="Русский перевод")]
    en: Annotated[TagTranslationSchema, Field(title="Английский перевод")]


class TagTranslationsResponseSchema(CamelCaseSchema):
    ru: Annotated[TagTranslationSchema, Field(title="Русский перевод")]
    en: Annotated[TagTranslationSchema, Field(title="Английский перевод")]

    @classmethod
    def from_domain_schema(cls, *, schema: Tag) -> Self:
        return cls(
            ru=TagTranslationSchema(name=schema.name_ru),
            en=TagTranslationSchema(name=schema.name_en),
        )


class TagsResponseSchema(CamelCaseSchema):
    tags: Annotated[list[TagResponseSchema], Field(title="Теги")]

    @classmethod
    def from_domain_schema(cls, *, schema: Tags, language: LanguageEnum) -> Self:
        return cls(
            tags=[
                TagResponseSchema.from_domain_schema(schema=tag, language=language)
                for tag in schema
            ],
        )


class TagRequestSchema(CamelCaseSchema):
    slug: Annotated[str, Field(title="Slug", min_length=1, max_length=255)]
    translations: Annotated[TagTranslationsSchema, Field(title="Переводы")]

    def to_create_schema(self, *, tag_id: IntId) -> TagCreateParams:
        return TagCreateParams(
            id=tag_id,
            name_ru=self.translations.ru.name,
            name_en=self.translations.en.name,
            slug=self.slug,
        )

    def to_update_schema(self) -> TagUpdateParams:
        return TagUpdateParams(
            name_ru=self.translations.ru.name,
            name_en=self.translations.en.name,
            slug=self.slug,
        )


class NoteReactionCountsResponseSchema(CamelCaseSchema):
    heart: Annotated[int, Field(title="Реакция: понравилось")]
    fire: Annotated[int, Field(title="Реакция: хочу ещё")]
    thinking: Annotated[int, Field(title="Реакция: заставило подумать")]
    neutral: Annotated[int, Field(title="Реакция: нормально")]
    poop: Annotated[int, Field(title="Реакция: не зашло")]

    @classmethod
    def from_domain_schema(cls, *, schema: NoteReactionCounts) -> Self:
        return cls(
            heart=schema.heart,
            fire=schema.fire,
            thinking=schema.thinking,
            neutral=schema.neutral,
            poop=schema.poop,
        )


class NoteSummaryResponseSchema(CamelCaseSchema):
    id: Annotated[str, Field(title="Идентификатор")]
    title: Annotated[str, Field(title="Заголовок")]
    slug: Annotated[str, Field(title="Slug")]
    folder: Annotated[str, Field(title="Папка")]
    author_username: Annotated[str, Field(title="Автор")]
    published_at: Annotated[str | None, Field(title="Дата публикации")]
    publish_status: Annotated[PublishStatusEnum, Field(title="Статус публикации")]
    updated_at: Annotated[str, Field(title="Дата обновления")]
    excerpt: Annotated[str, Field(title="Короткое превью")]
    tags: Annotated[list[TagResponseSchema], Field(title="Теги")]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        schema: Note,
        language: LanguageEnum,
    ) -> Self:
        return cls(
            id=str(schema.id),
            title=schema.localized_title(language=language),
            slug=schema.slug,
            folder=schema.localized_folder(language=language),
            author_username=schema.author_username,
            published_at=schema.published_at.isoformat()
            if schema.published_at is not None
            else None,
            publish_status=schema.publish_status,
            updated_at=schema.updated_at.isoformat(),
            excerpt=cls.build_excerpt(content=schema.localized_content(language=language)),
            tags=[
                TagResponseSchema.from_domain_schema(schema=tag, language=language)
                for tag in schema.tags
            ],
        )

    @classmethod
    def build_excerpt(cls, *, content: str) -> str:
        text = re.sub(r"[`*_#>\-[\]()!]", " ", content)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:180]


class NoteDetailResponseSchema(NoteSummaryResponseSchema):
    content: Annotated[str, Field(title="Содержимое")]
    created_at: Annotated[str, Field(title="Дата создания")]
    translations: Annotated[NoteTranslationsResponseSchema, Field(title="Переводы")]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        schema: Note,
        language: LanguageEnum,
    ) -> Self:
        summary = NoteSummaryResponseSchema.from_domain_schema(
            schema=schema,
            language=language,
        )
        return cls(
            **summary.model_dump(),
            content=schema.localized_content(language=language),
            created_at=schema.created_at.isoformat(),
            translations=NoteTranslationsResponseSchema.from_domain_schema(schema=schema),
        )


class NoteListResponseSchema(CamelCaseSchema):
    total_count: Annotated[int, Field(title="Количество заметок")]
    total_pages: Annotated[int, Field(title="Количество страниц")]
    notes: Annotated[list[NoteSummaryResponseSchema], Field(title="Заметки")]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        schema: Notes,
        language: LanguageEnum,
    ) -> Self:
        return cls(
            total_count=schema.total_count,
            total_pages=schema.total_pages,
            notes=[
                NoteSummaryResponseSchema.from_domain_schema(
                    schema=note,
                    language=language,
                )
                for note in schema.values
            ],
        )


class NotePublicStatsResponseSchema(CamelCaseSchema):
    note_id: Annotated[str, Field(title="Идентификатор заметки")]
    view_count: Annotated[int, Field(title="Количество просмотров")]
    reaction_counts: Annotated[NoteReactionCountsResponseSchema, Field(title="Реакции")]

    @classmethod
    def from_domain_schema(cls, *, schema: NotePublicStats) -> Self:
        return cls(
            note_id=str(schema.note_id),
            view_count=schema.view_count,
            reaction_counts=NoteReactionCountsResponseSchema.from_domain_schema(
                schema=schema.reaction_counts,
            ),
        )


class NotePublicStatsCollectionResponseSchema(CamelCaseSchema):
    stats: Annotated[list[NotePublicStatsResponseSchema], Field(title="Публичная статистика")]

    @classmethod
    def from_domain_schema(cls, *, schema: NotePublicStatsCollection) -> Self:
        return cls(
            stats=[
                NotePublicStatsResponseSchema.from_domain_schema(schema=item)
                for item in schema.values
            ],
        )


class NoteTranslationSchema(CamelCaseSchema):
    title: Annotated[str, Field(title="Заголовок", min_length=1, max_length=255)]
    content: Annotated[str, Field(title="Содержимое", min_length=1)]
    folder: Annotated[str, Field(title="Папка", min_length=1, max_length=255)]


class NoteTranslationsSchema(CamelCaseSchema):
    ru: Annotated[NoteTranslationSchema, Field(title="Русский перевод")]
    en: Annotated[NoteTranslationSchema, Field(title="Английский перевод")]


class NoteTranslationsResponseSchema(CamelCaseSchema):
    ru: Annotated[NoteTranslationSchema, Field(title="Русский перевод")]
    en: Annotated[NoteTranslationSchema, Field(title="Английский перевод")]

    @classmethod
    def from_domain_schema(cls, *, schema: Note) -> Self:
        return cls(
            ru=NoteTranslationSchema(
                title=schema.title_ru,
                content=schema.content_ru,
                folder=schema.folder_ru,
            ),
            en=NoteTranslationSchema(
                title=schema.title_en,
                content=schema.content_en,
                folder=schema.folder_en,
            ),
        )


class NoteRequestSchema(CamelCaseSchema):
    slug: Annotated[str, Field(title="Slug", min_length=1, max_length=255)]
    publish_status: Annotated[PublishStatusEnum, Field(title="Статус публикации")]
    tag_ids: Annotated[list[int], Field(title="Идентификаторы тегов")]
    translations: Annotated[NoteTranslationsSchema, Field(title="Переводы")]

    def to_create_schema(self, *, note_id: uuid.UUID, author_username: str) -> NoteCreateParams:
        return NoteCreateParams(
            id=note_id,
            slug=self.slug,
            title_ru=self.translations.ru.title,
            title_en=self.translations.en.title,
            content_ru=self.translations.ru.content,
            content_en=self.translations.en.content,
            folder_ru=self.translations.ru.folder,
            folder_en=self.translations.en.folder,
            author_username=author_username,
            publish_status=self.publish_status,
            tag_ids=[IntId(tag_id) for tag_id in self.tag_ids],
        )

    def to_update_schema(self) -> NoteUpdateParams:
        return NoteUpdateParams(
            slug=self.slug,
            title_ru=self.translations.ru.title,
            title_en=self.translations.en.title,
            content_ru=self.translations.ru.content,
            content_en=self.translations.en.content,
            folder_ru=self.translations.ru.folder,
            folder_en=self.translations.en.folder,
            publish_status=self.publish_status,
            tag_ids=[IntId(tag_id) for tag_id in self.tag_ids],
        )


class NoteReactionRequestSchema(CamelCaseSchema):
    reaction_kind: Annotated[NoteReactionKind | None, Field(title="Реакция")]
    client_token: Annotated[
        str,
        Field(title="Анонимный клиентский токен", min_length=1, max_length=255),
    ]


class NoteTreeItemResponseSchema(CamelCaseSchema):
    title: Annotated[str, Field(title="Заголовок")]
    slug: Annotated[str, Field(title="Slug")]
    publish_status: Annotated[PublishStatusEnum, Field(title="Статус публикации")]
    published_at: Annotated[str | None, Field(title="Дата публикации")]
    updated_at: Annotated[str, Field(title="Дата обновления")]

    @classmethod
    def from_domain_schema(cls, *, schema: NoteTreeItem) -> Self:
        return cls(
            title=schema.title,
            slug=schema.slug,
            publish_status=schema.publish_status,
            published_at=schema.published_at.isoformat()
            if schema.published_at is not None
            else None,
            updated_at=schema.updated_at.isoformat(),
        )


class NoteTreeFolderResponseSchema(CamelCaseSchema):
    folder: Annotated[str, Field(title="Папка")]
    notes: Annotated[list[NoteTreeItemResponseSchema], Field(title="Заметки")]

    @classmethod
    def from_domain_schema(cls, *, schema: NoteTreeFolder) -> Self:
        return cls(
            folder=schema.folder,
            notes=[
                NoteTreeItemResponseSchema.from_domain_schema(schema=note) for note in schema.notes
            ],
        )


class NoteTreeResponseSchema(CamelCaseSchema):
    folders: Annotated[list[NoteTreeFolderResponseSchema], Field(title="Папки")]

    @classmethod
    def from_domain_schema(cls, *, schema: NoteTree) -> Self:
        return cls(
            folders=[
                NoteTreeFolderResponseSchema.from_domain_schema(schema=folder)
                for folder in schema.folders
            ],
        )


class NoteAnalyticsTotalsResponseSchema(CamelCaseSchema):
    view_count: Annotated[int, Field(title="Количество просмотров")]
    engaged_view_count: Annotated[int, Field(title="Количество вовлечённых просмотров")]
    reaction_count: Annotated[int, Field(title="Количество реакций")]

    @classmethod
    def from_domain_schema(cls, *, schema: NoteAnalyticsTotals) -> Self:
        return cls(
            view_count=schema.view_count,
            engaged_view_count=schema.engaged_view_count,
            reaction_count=schema.reaction_count,
        )


class NoteAnalyticsNoteStatsResponseSchema(CamelCaseSchema):
    note_id: Annotated[str, Field(title="Идентификатор заметки")]
    title: Annotated[str, Field(title="Заголовок")]
    slug: Annotated[str, Field(title="Slug")]
    view_count: Annotated[int, Field(title="Количество просмотров")]
    engaged_view_count: Annotated[int, Field(title="Количество вовлечённых просмотров")]
    reaction_counts: Annotated[NoteReactionCountsResponseSchema, Field(title="Реакции")]

    @classmethod
    def from_domain_schema(cls, *, schema: NoteAnalyticsNoteStats) -> Self:
        return cls(
            note_id=str(schema.note_id),
            title=schema.title,
            slug=schema.slug,
            view_count=schema.view_count,
            engaged_view_count=schema.engaged_view_count,
            reaction_counts=NoteReactionCountsResponseSchema.from_domain_schema(
                schema=schema.reaction_counts,
            ),
        )


class NoteAnalyticsDailyStatsResponseSchema(CamelCaseSchema):
    note_id: Annotated[str, Field(title="Идентификатор заметки")]
    title: Annotated[str, Field(title="Заголовок")]
    slug: Annotated[str, Field(title="Slug")]
    date: Annotated[date, Field(title="Дата")]
    source_category: Annotated[NoteViewSourceCategory, Field(title="Источник")]
    view_count: Annotated[int, Field(title="Количество просмотров")]
    engaged_view_count: Annotated[int, Field(title="Количество вовлечённых просмотров")]

    @classmethod
    def from_domain_schema(cls, *, schema: NoteAnalyticsDailyStats) -> Self:
        return cls(
            note_id=str(schema.note_id),
            title=schema.title,
            slug=schema.slug,
            date=schema.date,
            source_category=schema.source_category,
            view_count=schema.view_count,
            engaged_view_count=schema.engaged_view_count,
        )


class NoteAnalyticsStatsResponseSchema(CamelCaseSchema):
    date_from: Annotated[date, Field(title="Дата начала")]
    date_to: Annotated[date, Field(title="Дата окончания")]
    totals: Annotated[NoteAnalyticsTotalsResponseSchema, Field(title="Итого")]
    notes: Annotated[list[NoteAnalyticsNoteStatsResponseSchema], Field(title="Заметки")]
    daily: Annotated[list[NoteAnalyticsDailyStatsResponseSchema], Field(title="Дни")]

    @classmethod
    def from_domain_schema(cls, *, schema: NoteAnalyticsStats) -> Self:
        return cls(
            date_from=schema.date_from,
            date_to=schema.date_to,
            totals=NoteAnalyticsTotalsResponseSchema.from_domain_schema(schema=schema.totals),
            notes=[
                NoteAnalyticsNoteStatsResponseSchema.from_domain_schema(schema=note)
                for note in schema.notes
            ],
            daily=[
                NoteAnalyticsDailyStatsResponseSchema.from_domain_schema(schema=item)
                for item in schema.daily
            ],
        )
