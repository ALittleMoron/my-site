import re
import uuid
from datetime import date
from typing import Annotated, Self

from pydantic import Field

from core.articles.enums import ArticleReactionKind, ArticleViewSourceCategory
from core.articles.schemas import (
    Article,
    ArticleAnalyticsArticleStats,
    ArticleAnalyticsDailyStats,
    ArticleAnalyticsStats,
    ArticleAnalyticsTotals,
    ArticleCreateParams,
    ArticleMetadata,
    ArticlePublicStats,
    ArticlePublicStatsCollection,
    ArticleReactionCounts,
    Articles,
    ArticleTree,
    ArticleTreeFolder,
    ArticleTreeItem,
    ArticleUpdateParams,
    Tag,
    TagCreateParams,
    Tags,
    TagUpdateParams,
)
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
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


class ArticleReactionCountsResponseSchema(CamelCaseSchema):
    heart: Annotated[int, Field(title="Реакция: понравилось")]
    fire: Annotated[int, Field(title="Реакция: хочу ещё")]
    thinking: Annotated[int, Field(title="Реакция: заставило подумать")]
    neutral: Annotated[int, Field(title="Реакция: нормально")]
    poop: Annotated[int, Field(title="Реакция: не зашло")]

    @classmethod
    def from_domain_schema(cls, *, schema: ArticleReactionCounts) -> Self:
        return cls(
            heart=schema.heart,
            fire=schema.fire,
            thinking=schema.thinking,
            neutral=schema.neutral,
            poop=schema.poop,
        )


class ArticleMetadataSchema(CamelCaseSchema):
    seo_title_ru: Annotated[str | None, Field(title="SEO заголовок RU", max_length=255)]
    seo_title_en: Annotated[str | None, Field(title="SEO заголовок EN", max_length=255)]
    seo_description_ru: Annotated[str | None, Field(title="SEO описание RU", max_length=320)]
    seo_description_en: Annotated[str | None, Field(title="SEO описание EN", max_length=320)]
    cover_image_url: Annotated[str | None, Field(title="URL обложки", max_length=2048)]
    cover_image_alt_ru: Annotated[str | None, Field(title="Alt обложки RU", max_length=255)]
    cover_image_alt_en: Annotated[str | None, Field(title="Alt обложки EN", max_length=255)]

    def to_domain_schema(self) -> ArticleMetadata:
        return ArticleMetadata(
            seo_title_ru=self.seo_title_ru,
            seo_title_en=self.seo_title_en,
            seo_description_ru=self.seo_description_ru,
            seo_description_en=self.seo_description_en,
            cover_image_url=self.cover_image_url,
            cover_image_alt_ru=self.cover_image_alt_ru,
            cover_image_alt_en=self.cover_image_alt_en,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ArticleMetadata) -> Self:
        return cls(
            seo_title_ru=schema.seo_title_ru,
            seo_title_en=schema.seo_title_en,
            seo_description_ru=schema.seo_description_ru,
            seo_description_en=schema.seo_description_en,
            cover_image_url=schema.cover_image_url,
            cover_image_alt_ru=schema.cover_image_alt_ru,
            cover_image_alt_en=schema.cover_image_alt_en,
        )


class ArticleSummaryResponseSchema(CamelCaseSchema):
    id: Annotated[str, Field(title="Идентификатор")]
    title: Annotated[str, Field(title="Заголовок")]
    slug: Annotated[str, Field(title="Slug")]
    folder: Annotated[str, Field(title="Папка")]
    author_username: Annotated[str, Field(title="Автор")]
    published_at: Annotated[str | None, Field(title="Дата публикации")]
    publish_status: Annotated[PublishStatusEnum, Field(title="Статус публикации")]
    updated_at: Annotated[str, Field(title="Дата обновления")]
    excerpt: Annotated[str, Field(title="Короткое превью")]
    metadata: Annotated[ArticleMetadataSchema, Field(title="SEO metadata")]
    tags: Annotated[list[TagResponseSchema], Field(title="Теги")]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        schema: Article,
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
            metadata=ArticleMetadataSchema.from_domain_schema(schema=schema.metadata),
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


class ArticleDetailResponseSchema(ArticleSummaryResponseSchema):
    content: Annotated[str, Field(title="Содержимое")]
    created_at: Annotated[str, Field(title="Дата создания")]
    translations: Annotated[ArticleTranslationsResponseSchema, Field(title="Переводы")]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        schema: Article,
        language: LanguageEnum,
    ) -> Self:
        summary = ArticleSummaryResponseSchema.from_domain_schema(
            schema=schema,
            language=language,
        )
        return cls(
            **summary.model_dump(),
            content=schema.localized_content(language=language),
            created_at=schema.created_at.isoformat(),
            translations=ArticleTranslationsResponseSchema.from_domain_schema(schema=schema),
        )


class ArticleListResponseSchema(CamelCaseSchema):
    total_count: Annotated[int, Field(title="Количество статей")]
    total_pages: Annotated[int, Field(title="Количество страниц")]
    articles: Annotated[list[ArticleSummaryResponseSchema], Field(title="Статьи")]

    @classmethod
    def from_domain_schema(
        cls,
        *,
        schema: Articles,
        language: LanguageEnum,
    ) -> Self:
        return cls(
            total_count=schema.total_count,
            total_pages=schema.total_pages,
            articles=[
                ArticleSummaryResponseSchema.from_domain_schema(
                    schema=article,
                    language=language,
                )
                for article in schema.values
            ],
        )


class ArticlePublicStatsResponseSchema(CamelCaseSchema):
    article_id: Annotated[str, Field(title="Идентификатор статьи")]
    view_count: Annotated[int, Field(title="Количество просмотров")]
    reaction_counts: Annotated[ArticleReactionCountsResponseSchema, Field(title="Реакции")]

    @classmethod
    def from_domain_schema(cls, *, schema: ArticlePublicStats) -> Self:
        return cls(
            article_id=str(schema.article_id),
            view_count=schema.view_count,
            reaction_counts=ArticleReactionCountsResponseSchema.from_domain_schema(
                schema=schema.reaction_counts,
            ),
        )


class ArticlePublicStatsCollectionResponseSchema(CamelCaseSchema):
    stats: Annotated[list[ArticlePublicStatsResponseSchema], Field(title="Публичная статистика")]

    @classmethod
    def from_domain_schema(cls, *, schema: ArticlePublicStatsCollection) -> Self:
        return cls(
            stats=[
                ArticlePublicStatsResponseSchema.from_domain_schema(schema=item)
                for item in schema.values
            ],
        )


class ArticleTranslationSchema(CamelCaseSchema):
    title: Annotated[str, Field(title="Заголовок", min_length=1, max_length=255)]
    content: Annotated[str, Field(title="Содержимое", min_length=1)]
    folder: Annotated[str, Field(title="Папка", min_length=1, max_length=255)]


class ArticleTranslationsSchema(CamelCaseSchema):
    ru: Annotated[ArticleTranslationSchema, Field(title="Русский перевод")]
    en: Annotated[ArticleTranslationSchema, Field(title="Английский перевод")]


class ArticleTranslationsResponseSchema(CamelCaseSchema):
    ru: Annotated[ArticleTranslationSchema, Field(title="Русский перевод")]
    en: Annotated[ArticleTranslationSchema, Field(title="Английский перевод")]

    @classmethod
    def from_domain_schema(cls, *, schema: Article) -> Self:
        return cls(
            ru=ArticleTranslationSchema(
                title=schema.title_ru,
                content=schema.content_ru,
                folder=schema.folder_ru,
            ),
            en=ArticleTranslationSchema(
                title=schema.title_en,
                content=schema.content_en,
                folder=schema.folder_en,
            ),
        )


class ArticleRequestSchema(CamelCaseSchema):
    slug: Annotated[str, Field(title="Slug", min_length=1, max_length=255)]
    publish_status: Annotated[PublishStatusEnum, Field(title="Статус публикации")]
    tag_ids: Annotated[list[int], Field(title="Идентификаторы тегов")]
    translations: Annotated[ArticleTranslationsSchema, Field(title="Переводы")]
    metadata: Annotated[ArticleMetadataSchema, Field(title="SEO metadata")]

    def to_create_schema(
        self,
        *,
        article_id: uuid.UUID,
        author_username: str,
    ) -> ArticleCreateParams:
        return ArticleCreateParams(
            id=article_id,
            slug=self.slug,
            title_ru=self.translations.ru.title,
            title_en=self.translations.en.title,
            content_ru=self.translations.ru.content,
            content_en=self.translations.en.content,
            folder_ru=self.translations.ru.folder,
            folder_en=self.translations.en.folder,
            author_username=author_username,
            publish_status=self.publish_status,
            metadata=self.metadata.to_domain_schema(),
            tag_ids=[IntId(tag_id) for tag_id in self.tag_ids],
        )

    def to_update_schema(self) -> ArticleUpdateParams:
        return ArticleUpdateParams(
            slug=self.slug,
            title_ru=self.translations.ru.title,
            title_en=self.translations.en.title,
            content_ru=self.translations.ru.content,
            content_en=self.translations.en.content,
            folder_ru=self.translations.ru.folder,
            folder_en=self.translations.en.folder,
            publish_status=self.publish_status,
            metadata=self.metadata.to_domain_schema(),
            tag_ids=[IntId(tag_id) for tag_id in self.tag_ids],
        )


class ArticleReactionRequestSchema(CamelCaseSchema):
    reaction_kind: Annotated[ArticleReactionKind | None, Field(title="Реакция")]
    client_token: Annotated[
        str,
        Field(title="Анонимный клиентский токен", min_length=1, max_length=255),
    ]


class ArticleTreeItemResponseSchema(CamelCaseSchema):
    title: Annotated[str, Field(title="Заголовок")]
    slug: Annotated[str, Field(title="Slug")]
    publish_status: Annotated[PublishStatusEnum, Field(title="Статус публикации")]
    published_at: Annotated[str | None, Field(title="Дата публикации")]
    updated_at: Annotated[str, Field(title="Дата обновления")]

    @classmethod
    def from_domain_schema(cls, *, schema: ArticleTreeItem) -> Self:
        return cls(
            title=schema.title,
            slug=schema.slug,
            publish_status=schema.publish_status,
            published_at=schema.published_at.isoformat()
            if schema.published_at is not None
            else None,
            updated_at=schema.updated_at.isoformat(),
        )


class ArticleTreeFolderResponseSchema(CamelCaseSchema):
    folder: Annotated[str, Field(title="Папка")]
    articles: Annotated[list[ArticleTreeItemResponseSchema], Field(title="Статьи")]

    @classmethod
    def from_domain_schema(cls, *, schema: ArticleTreeFolder) -> Self:
        return cls(
            folder=schema.folder,
            articles=[
                ArticleTreeItemResponseSchema.from_domain_schema(schema=article)
                for article in schema.articles
            ],
        )


class ArticleTreeResponseSchema(CamelCaseSchema):
    folders: Annotated[list[ArticleTreeFolderResponseSchema], Field(title="Папки")]

    @classmethod
    def from_domain_schema(cls, *, schema: ArticleTree) -> Self:
        return cls(
            folders=[
                ArticleTreeFolderResponseSchema.from_domain_schema(schema=folder)
                for folder in schema.folders
            ],
        )


class ArticleAnalyticsTotalsResponseSchema(CamelCaseSchema):
    view_count: Annotated[int, Field(title="Количество просмотров")]
    engaged_view_count: Annotated[int, Field(title="Количество вовлечённых просмотров")]
    reaction_count: Annotated[int, Field(title="Количество реакций")]

    @classmethod
    def from_domain_schema(cls, *, schema: ArticleAnalyticsTotals) -> Self:
        return cls(
            view_count=schema.view_count,
            engaged_view_count=schema.engaged_view_count,
            reaction_count=schema.reaction_count,
        )


class ArticleAnalyticsArticleStatsResponseSchema(CamelCaseSchema):
    article_id: Annotated[str, Field(title="Идентификатор статьи")]
    title: Annotated[str, Field(title="Заголовок")]
    slug: Annotated[str, Field(title="Slug")]
    view_count: Annotated[int, Field(title="Количество просмотров")]
    engaged_view_count: Annotated[int, Field(title="Количество вовлечённых просмотров")]
    reaction_counts: Annotated[ArticleReactionCountsResponseSchema, Field(title="Реакции")]

    @classmethod
    def from_domain_schema(cls, *, schema: ArticleAnalyticsArticleStats) -> Self:
        return cls(
            article_id=str(schema.article_id),
            title=schema.title,
            slug=schema.slug,
            view_count=schema.view_count,
            engaged_view_count=schema.engaged_view_count,
            reaction_counts=ArticleReactionCountsResponseSchema.from_domain_schema(
                schema=schema.reaction_counts,
            ),
        )


class ArticleAnalyticsDailyStatsResponseSchema(CamelCaseSchema):
    article_id: Annotated[str, Field(title="Идентификатор статьи")]
    title: Annotated[str, Field(title="Заголовок")]
    slug: Annotated[str, Field(title="Slug")]
    date: Annotated[date, Field(title="Дата")]
    source_category: Annotated[ArticleViewSourceCategory, Field(title="Источник")]
    view_count: Annotated[int, Field(title="Количество просмотров")]
    engaged_view_count: Annotated[int, Field(title="Количество вовлечённых просмотров")]

    @classmethod
    def from_domain_schema(cls, *, schema: ArticleAnalyticsDailyStats) -> Self:
        return cls(
            article_id=str(schema.article_id),
            title=schema.title,
            slug=schema.slug,
            date=schema.date,
            source_category=schema.source_category,
            view_count=schema.view_count,
            engaged_view_count=schema.engaged_view_count,
        )


class ArticleAnalyticsStatsResponseSchema(CamelCaseSchema):
    date_from: Annotated[date, Field(title="Дата начала")]
    date_to: Annotated[date, Field(title="Дата окончания")]
    totals: Annotated[ArticleAnalyticsTotalsResponseSchema, Field(title="Итого")]
    articles: Annotated[list[ArticleAnalyticsArticleStatsResponseSchema], Field(title="Статьи")]
    daily: Annotated[list[ArticleAnalyticsDailyStatsResponseSchema], Field(title="Дни")]

    @classmethod
    def from_domain_schema(cls, *, schema: ArticleAnalyticsStats) -> Self:
        return cls(
            date_from=schema.date_from,
            date_to=schema.date_to,
            totals=ArticleAnalyticsTotalsResponseSchema.from_domain_schema(schema=schema.totals),
            articles=[
                ArticleAnalyticsArticleStatsResponseSchema.from_domain_schema(schema=article)
                for article in schema.articles
            ],
            daily=[
                ArticleAnalyticsDailyStatsResponseSchema.from_domain_schema(schema=item)
                for item in schema.daily
            ],
        )
