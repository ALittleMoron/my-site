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
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_dev_utils.mixins.audit import AuditMixin
from sqlalchemy_dev_utils.mixins.ids import IntegerIDMixin, UUIDMixin
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

from core.enums import PublishStatusEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from core.notes.schemas import Note, Tag, Tags
from core.types import IntId
from infra.postgresql.models.base import BaseModel
from infra.postgresql.models.mixins.publish import PublishMixin


class NoteModel(PublishMixin, UUIDMixin, AuditMixin, BaseModel):
    title_ru: Mapped[str] = mapped_column(
        String(length=255),
        doc="Russian title of the note",
    )
    title_en: Mapped[str] = mapped_column(
        String(length=255),
        doc="English title of the note",
    )
    content_ru: Mapped[str] = mapped_column(
        String(),
        doc="Russian content of the note",
    )
    content_en: Mapped[str] = mapped_column(
        String(),
        doc="English content of the note",
    )
    slug: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        index=True,
        doc="URL slug for the note",
    )
    folder_ru: Mapped[str] = mapped_column(
        String(length=255),
        doc="Russian one-level folder name for the note tree",
    )
    folder_en: Mapped[str] = mapped_column(
        String(length=255),
        doc="English one-level folder name for the note tree",
    )
    author_username: Mapped[str] = mapped_column(
        String(length=255),
        doc="Username of the note author",
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

    tag_links: Mapped[list[NoteToTagSecondaryModel]] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
        doc="Links between notes and tags",
    )

    __table_args__ = (
        Index(
            "notes_note_search_vector_gin_idx",
            search_vector_ru,
            postgresql_using="gin",
        ),
        Index(
            "notes_note_search_vector_en_gin_idx",
            search_vector_en,
            postgresql_using="gin",
        ),
        Index(
            "notes_note_publish_status_published_at_idx",
            "publish_status",
            "published_at",
        ),
    )

    def __str__(self) -> str:
        return f'Note "{self.title_en}"'

    @classmethod
    def from_domain_schema(cls, note: Note) -> Self:
        return cls(
            id=note.id,
            title_ru=note.title_ru,
            title_en=note.title_en,
            content_ru=note.content_ru,
            content_en=note.content_en,
            slug=note.slug,
            folder_ru=note.folder_ru,
            folder_en=note.folder_en,
            author_username=note.author_username,
            published_at=note.published_at,
            publish_status=note.publish_status,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )

    def update_from_domain_schema(self, note: Note) -> None:
        self.title_ru = note.title_ru
        self.title_en = note.title_en
        self.content_ru = note.content_ru
        self.content_en = note.content_en
        self.slug = note.slug
        self.folder_ru = note.folder_ru
        self.folder_en = note.folder_en
        self.publish_status = note.publish_status
        self.published_at = note.published_at
        self.updated_at = note.updated_at

    def to_domain_schema(self, *, include_deleted_tags: bool) -> Note:
        return Note(
            id=self.id,
            slug=self.slug,
            title_ru=self.title_ru,
            title_en=self.title_en,
            content_ru=self.content_ru,
            content_en=self.content_en,
            folder_ru=self.folder_ru,
            folder_en=self.folder_en,
            author_username=self.author_username,
            published_at=self.published_at,
            publish_status=PublishStatusEnum.from_storage_value(self.publish_status),
            created_at=self.created_at,
            updated_at=self.updated_at,
            tags=Tags(
                values=[
                    link.tag.to_domain_schema()
                    for link in self.tag_links
                    if include_deleted_tags or link.tag.deleted_at is None
                ],
            ),
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
            "notes_tag_name_ru_trgm_idx",
            func.lower(name_ru).label("name_ru_lower"),
            postgresql_using="gin",
            postgresql_ops={"name_ru_lower": "gin_trgm_ops"},
        ),
        Index(
            "notes_tag_name_en_trgm_idx",
            func.lower(name_en).label("name_en_lower"),
            postgresql_using="gin",
            postgresql_ops={"name_en_lower": "gin_trgm_ops"},
        ),
        Index(
            "notes_tag_slug_trgm_idx",
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


class NoteToTagSecondaryModel(IntegerIDMixin, BaseModel):
    note_id: Mapped[UUID] = mapped_column(
        ForeignKey(NoteModel.id, ondelete="CASCADE"),
        doc="Note identifier",
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey(TagModel.id, ondelete="CASCADE"),
        doc="Tag identifier",
    )

    note: Mapped[NoteModel] = relationship(
        back_populates="tag_links",
        doc="Linked note",
    )
    tag: Mapped[TagModel] = relationship(
        doc="Linked tag",
    )

    __table_args__ = (UniqueConstraint("note_id", "tag_id", name="notes_note_tag_uniq"),)

    @classmethod
    def from_domain_schema(cls, tag: Tag) -> Self:
        return cls(
            tag_id=tag.id,
        )


class NoteDailyAnalyticsModel(IntegerIDMixin, BaseModel):
    note_id: Mapped[UUID] = mapped_column(
        ForeignKey(NoteModel.id, ondelete="CASCADE"),
        doc="Note identifier",
    )
    date: Mapped[date] = mapped_column(
        Date(),
        doc="UTC day when the note interaction was recorded",
    )
    source_category: Mapped[NoteViewSourceCategory] = mapped_column(
        Enum(
            NoteViewSourceCategory,
            native_enum=False,
            length=20,
            name="note_view_source_category_enum",
        ),
        doc="Coarse referrer source category",
    )
    view_count: Mapped[int] = mapped_column(
        Integer(),
        doc="Number of public note detail views",
    )
    engaged_view_count: Mapped[int] = mapped_column(
        Integer(),
        doc="Number of public note detail views with engagement signal",
    )

    note: Mapped[NoteModel] = relationship(doc="Tracked note")

    __table_args__ = (
        UniqueConstraint(
            "note_id",
            "date",
            "source_category",
            name="notes_daily_analytics_note_date_source_uniq",
        ),
    )


class NoteReactionModel(IntegerIDMixin, AuditMixin, BaseModel):
    note_id: Mapped[UUID] = mapped_column(
        ForeignKey(NoteModel.id, ondelete="CASCADE"),
        doc="Note identifier",
    )
    note_scoped_voter_hash: Mapped[str] = mapped_column(
        String(length=64),
        doc="HMAC hash scoped to one note and one anonymous client token",
    )
    reaction_kind: Mapped[NoteReactionKind] = mapped_column(
        Enum(
            NoteReactionKind,
            native_enum=False,
            length=20,
            name="note_reaction_kind_enum",
        ),
        doc="Anonymous reaction kind",
    )

    note: Mapped[NoteModel] = relationship(doc="Reacted note")

    __table_args__ = (
        UniqueConstraint(
            "note_id",
            "note_scoped_voter_hash",
            name="notes_reaction_note_voter_uniq",
        ),
    )
