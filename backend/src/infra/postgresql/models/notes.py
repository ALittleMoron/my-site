from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_dev_utils.mixins.audit import AuditMixin
from sqlalchemy_dev_utils.mixins.ids import IntegerIDMixin, UUIDMixin
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

from core.enums import PublishStatusEnum
from core.notes.schemas import Note, NoteTags, Tag
from core.types import IntId
from infra.postgresql.models.base import BaseModel
from infra.postgresql.models.mixins.publish import PublishMixin


class NoteModel(PublishMixin, UUIDMixin, AuditMixin, BaseModel):
    title: Mapped[str] = mapped_column(
        String(length=255),
        doc="Title of the note",
    )
    content: Mapped[str] = mapped_column(
        String(),
        doc="Content of the note",
    )
    slug: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        index=True,
        doc="URL slug for the note",
    )
    folder: Mapped[str] = mapped_column(
        String(length=255),
        doc="One-level folder name for the note tree",
    )
    author_username: Mapped[str] = mapped_column(
        String(length=255),
        doc="Username of the note author",
    )

    tag_links: Mapped[list[NoteToTagSecondaryModel]] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
        doc="Links between notes and tags",
    )

    def __str__(self) -> str:
        return f'Note "{self.title}"'

    @classmethod
    def from_domain_schema(cls, note: Note) -> Self:
        return cls(
            id=note.id,
            title=note.title,
            content=note.content,
            slug=note.slug,
            folder=note.folder,
            author_username=note.author_username,
            published_at=note.published_at,
            publish_status=note.publish_status,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )

    def update_from_domain_schema(self, note: Note) -> None:
        self.title = note.title
        self.content = note.content
        self.slug = note.slug
        self.folder = note.folder
        self.publish_status = note.publish_status
        self.published_at = note.published_at
        self.updated_at = note.updated_at

    def to_domain_schema(self, *, include_deleted_tags: bool) -> Note:
        return Note(
            id=self.id,
            title=self.title,
            content=self.content,
            slug=self.slug,
            folder=self.folder,
            author_username=self.author_username,
            published_at=self.published_at,
            publish_status=_to_publish_status(self.publish_status),
            created_at=self.created_at,
            updated_at=self.updated_at,
            tags=NoteTags(
                values=[
                    link.tag.to_domain_schema()
                    for link in self.tag_links
                    if include_deleted_tags or link.tag.deleted_at is None
                ],
            ),
        )


class TagModel(IntegerIDMixin, AuditMixin, BaseModel):
    name: Mapped[str] = mapped_column(
        String(length=255),
        doc="Human-readable tag name",
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

    def __str__(self) -> str:
        return f'Tag "{self.name}"'

    @classmethod
    def from_domain_schema(cls, tag: Tag) -> Self:
        return cls(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
            deleted_at=tag.deleted_at,
        )

    def update_from_domain_schema(self, tag: Tag) -> None:
        self.name = tag.name
        self.slug = tag.slug

    def to_domain_schema(self) -> Tag:
        return Tag(
            id=IntId(self.id),
            name=self.name,
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


def _to_publish_status(value: PublishStatusEnum | str) -> PublishStatusEnum:
    if isinstance(value, PublishStatusEnum):
        return value
    try:
        return PublishStatusEnum.from_value(value)
    except ValueError:
        return PublishStatusEnum[value]
