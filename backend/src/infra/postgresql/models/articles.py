from datetime import date, datetime
from typing import Self
from uuid import UUID

from sqlalchemy import (
    Computed,
    Date,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_dev_utils.mixins.audit import AuditMixin
from sqlalchemy_dev_utils.mixins.ids import IntegerIDMixin, UUIDMixin
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

from core.articles.enums import ArticleReactionKind, ArticleViewSourceCategory
from core.articles.schemas import Article, ArticleMetadata, Tag, Tags
from core.enums import PublishStatusEnum
from core.types import IntId
from infra.postgresql.models.base import BaseModel
from infra.postgresql.models.mixins.publish import PublishMixin


class ArticleModel(PublishMixin, UUIDMixin, AuditMixin, BaseModel):
    title_ru: Mapped[str] = mapped_column(
        String(length=255),
        doc="Russian title of the article",
    )
    title_en: Mapped[str] = mapped_column(
        String(length=255),
        doc="English title of the article",
    )
    content_ru: Mapped[str] = mapped_column(
        String(),
        doc="Russian content of the article",
    )
    content_en: Mapped[str] = mapped_column(
        String(),
        doc="English content of the article",
    )
    slug: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        index=True,
        doc="URL slug for the article",
    )
    folder_ru: Mapped[str] = mapped_column(
        String(length=255),
        doc="Russian one-level folder name for the article tree",
    )
    folder_en: Mapped[str] = mapped_column(
        String(length=255),
        doc="English one-level folder name for the article tree",
    )
    author_username: Mapped[str] = mapped_column(
        String(length=255),
        doc="Username of the article author",
    )
    seo_title_ru: Mapped[str | None] = mapped_column(
        String(length=255),
        doc="Russian SEO title override for the article",
    )
    seo_title_en: Mapped[str | None] = mapped_column(
        String(length=255),
        doc="English SEO title override for the article",
    )
    seo_description_ru: Mapped[str | None] = mapped_column(
        String(length=320),
        doc="Russian SEO description for the article",
    )
    seo_description_en: Mapped[str | None] = mapped_column(
        String(length=320),
        doc="English SEO description for the article",
    )
    cover_image_url: Mapped[str | None] = mapped_column(
        String(length=2048),
        doc="Public cover image URL for the article",
    )
    cover_image_alt_ru: Mapped[str | None] = mapped_column(
        String(length=255),
        doc="Russian cover image alt text",
    )
    cover_image_alt_en: Mapped[str | None] = mapped_column(
        String(length=255),
        doc="English cover image alt text",
    )
    search_vector_ru: Mapped[str] = mapped_column(
        TSVECTOR(),
        Computed(
            "setweight(to_tsvector('simple', coalesce(title_ru, '')), 'A') || "
            "setweight(to_tsvector('simple', coalesce(content_ru, '')), 'B')",
            persisted=True,
        ),
        doc="Generated full-text search vector for Russian title and content",
    )
    search_vector_en: Mapped[str] = mapped_column(
        TSVECTOR(),
        Computed(
            "setweight(to_tsvector('simple', coalesce(title_en, '')), 'A') || "
            "setweight(to_tsvector('simple', coalesce(content_en, '')), 'B')",
            persisted=True,
        ),
        doc="Generated full-text search vector for English title and content",
    )

    tag_links: Mapped[list[ArticleToTagSecondaryModel]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
        doc="Links between articles and tags",
    )

    __table_args__ = (
        Index(
            "articles_article_search_vector_gin_idx",
            search_vector_ru,
            postgresql_using="gin",
        ),
        Index(
            "articles_article_search_vector_en_gin_idx",
            search_vector_en,
            postgresql_using="gin",
        ),
        Index(
            "articles_article_publish_status_published_at_idx",
            "publish_status",
            "published_at",
        ),
        Index(
            "articles_article_publish_status_published_updated_idx",
            "publish_status",
            text("published_at DESC NULLS LAST"),
            text("updated_at DESC"),
        ),
        Index(
            "articles_article_tree_ru_published_idx",
            "folder_ru",
            text("published_at DESC NULLS LAST"),
            text("updated_at DESC"),
            "title_ru",
            postgresql_include=("slug", "publish_status"),
            postgresql_where=text("publish_status = 'PUBLISHED'"),
        ),
        Index(
            "articles_article_tree_en_published_idx",
            "folder_en",
            text("published_at DESC NULLS LAST"),
            text("updated_at DESC"),
            "title_en",
            postgresql_include=("slug", "publish_status"),
            postgresql_where=text("publish_status = 'PUBLISHED'"),
        ),
    )

    def __str__(self) -> str:
        return f'Article "{self.title_en}"'

    @classmethod
    def from_domain_schema(cls, article: Article) -> Self:
        return cls(
            id=article.id,
            title_ru=article.title_ru,
            title_en=article.title_en,
            content_ru=article.content_ru,
            content_en=article.content_en,
            slug=article.slug,
            folder_ru=article.folder_ru,
            folder_en=article.folder_en,
            author_username=article.author_username,
            seo_title_ru=article.metadata.seo_title_ru,
            seo_title_en=article.metadata.seo_title_en,
            seo_description_ru=article.metadata.seo_description_ru,
            seo_description_en=article.metadata.seo_description_en,
            cover_image_url=article.metadata.cover_image_url,
            cover_image_alt_ru=article.metadata.cover_image_alt_ru,
            cover_image_alt_en=article.metadata.cover_image_alt_en,
            published_at=article.published_at,
            publish_status=article.publish_status,
            created_at=article.created_at,
            updated_at=article.updated_at,
        )

    def update_from_domain_schema(self, article: Article) -> None:
        self.title_ru = article.title_ru
        self.title_en = article.title_en
        self.content_ru = article.content_ru
        self.content_en = article.content_en
        self.slug = article.slug
        self.folder_ru = article.folder_ru
        self.folder_en = article.folder_en
        self.seo_title_ru = article.metadata.seo_title_ru
        self.seo_title_en = article.metadata.seo_title_en
        self.seo_description_ru = article.metadata.seo_description_ru
        self.seo_description_en = article.metadata.seo_description_en
        self.cover_image_url = article.metadata.cover_image_url
        self.cover_image_alt_ru = article.metadata.cover_image_alt_ru
        self.cover_image_alt_en = article.metadata.cover_image_alt_en
        self.publish_status = article.publish_status
        self.published_at = article.published_at
        self.updated_at = article.updated_at

    def to_domain_schema(self, *, include_deleted_tags: bool, include_tags: bool) -> Article:
        return Article(
            id=self.id,
            slug=self.slug,
            title_ru=self.title_ru,
            title_en=self.title_en,
            content_ru=self.content_ru,
            content_en=self.content_en,
            folder_ru=self.folder_ru,
            folder_en=self.folder_en,
            author_username=self.author_username,
            metadata=self.to_metadata_domain_schema(),
            published_at=self.published_at,
            publish_status=PublishStatusEnum.from_storage_value(self.publish_status),
            created_at=self.created_at,
            updated_at=self.updated_at,
            tags=Tags(
                values=[
                    link.tag.to_domain_schema()
                    for link in self.tag_links
                    if include_deleted_tags or link.tag.deleted_at is None
                ]
                if include_tags
                else [],
            ),
        )

    def to_metadata_domain_schema(self) -> ArticleMetadata:
        return ArticleMetadata(
            seo_title_ru=self.seo_title_ru,
            seo_title_en=self.seo_title_en,
            seo_description_ru=self.seo_description_ru,
            seo_description_en=self.seo_description_en,
            cover_image_url=self.cover_image_url,
            cover_image_alt_ru=self.cover_image_alt_ru,
            cover_image_alt_en=self.cover_image_alt_en,
        )


class TagModel(IntegerIDMixin, AuditMixin, BaseModel):
    name_ru: Mapped[str] = mapped_column(
        String(length=255),
        doc="Russian human-readable tag name",
    )
    name_en: Mapped[str] = mapped_column(
        String(length=255),
        doc="English human-readable tag name",
    )
    slug: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        index=True,
        doc="Stable tag slug used in filters",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime(timezone=True),
        doc="Soft deletion timestamp",
    )

    __table_args__ = (
        Index(
            "articles_tag_name_ru_trgm_idx",
            func.lower(name_ru).label("name_ru_lower"),
            postgresql_using="gin",
            postgresql_ops={"name_ru_lower": "gin_trgm_ops"},
        ),
        Index(
            "articles_tag_name_en_trgm_idx",
            func.lower(name_en).label("name_en_lower"),
            postgresql_using="gin",
            postgresql_ops={"name_en_lower": "gin_trgm_ops"},
        ),
        Index(
            "articles_tag_slug_trgm_idx",
            func.lower(slug).label("slug_lower"),
            postgresql_using="gin",
            postgresql_ops={"slug_lower": "gin_trgm_ops"},
        ),
    )

    def __str__(self) -> str:
        return f'Tag "{self.name_en}"'

    @classmethod
    def from_domain_schema(cls, tag: Tag) -> Self:
        return cls(
            id=tag.id,
            name_ru=tag.name_ru,
            name_en=tag.name_en,
            slug=tag.slug,
            deleted_at=tag.deleted_at,
        )

    def update_from_domain_schema(self, tag: Tag) -> None:
        self.name_ru = tag.name_ru
        self.name_en = tag.name_en
        self.slug = tag.slug

    def to_domain_schema(self) -> Tag:
        return Tag(
            id=IntId(self.id),
            name_ru=self.name_ru,
            name_en=self.name_en,
            slug=self.slug,
            deleted_at=self.deleted_at,
        )


class ArticleToTagSecondaryModel(IntegerIDMixin, BaseModel):
    article_id: Mapped[UUID] = mapped_column(
        ForeignKey(ArticleModel.id, ondelete="CASCADE"),
        doc="Article identifier",
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey(TagModel.id, ondelete="CASCADE"),
        doc="Tag identifier",
    )

    article: Mapped[ArticleModel] = relationship(
        back_populates="tag_links",
        doc="Linked article",
    )
    tag: Mapped[TagModel] = relationship(
        doc="Linked tag",
    )

    __table_args__ = (UniqueConstraint("article_id", "tag_id", name="articles_article_tag_uniq"),)

    @classmethod
    def from_domain_schema(cls, tag: Tag) -> Self:
        return cls(
            tag_id=tag.id,
        )


class ArticleDailyAnalyticsModel(IntegerIDMixin, BaseModel):
    article_id: Mapped[UUID] = mapped_column(
        ForeignKey(ArticleModel.id, ondelete="CASCADE"),
        doc="Article identifier",
    )
    date: Mapped[date] = mapped_column(
        Date(),
        doc="UTC day when the article interaction was recorded",
    )
    source_category: Mapped[ArticleViewSourceCategory] = mapped_column(
        Enum(
            ArticleViewSourceCategory,
            native_enum=True,
            name="article_view_source_category_enum",
        ),
        doc="Coarse referrer source category",
    )
    view_count: Mapped[int] = mapped_column(
        Integer(),
        doc="Number of public article detail views",
    )
    engaged_view_count: Mapped[int] = mapped_column(
        Integer(),
        doc="Number of public article detail views with engagement signal",
    )

    article: Mapped[ArticleModel] = relationship(doc="Tracked article")

    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "date",
            "source_category",
            name="articles_daily_analytics_article_date_source_uniq",
        ),
    )


class ArticleReactionModel(IntegerIDMixin, AuditMixin, BaseModel):
    article_id: Mapped[UUID] = mapped_column(
        ForeignKey(ArticleModel.id, ondelete="CASCADE"),
        doc="Article identifier",
    )
    article_scoped_voter_hash: Mapped[str] = mapped_column(
        String(length=64),
        doc="HMAC hash scoped to one article and one anonymous client token",
    )
    reaction_kind: Mapped[ArticleReactionKind] = mapped_column(
        Enum(
            ArticleReactionKind,
            native_enum=True,
            name="article_reaction_kind_enum",
        ),
        doc="Anonymous reaction kind",
    )

    article: Mapped[ArticleModel] = relationship(doc="Reacted article")

    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "article_scoped_voter_hash",
            name="articles_reaction_article_voter_uniq",
        ),
    )
