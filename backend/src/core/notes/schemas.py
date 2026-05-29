from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from core.enums import PublishStatusEnum
from core.schemas import ValuedDataclass
from core.types import IntId


@dataclass(frozen=True, slots=True, kw_only=True)
class Tag:
    id: IntId
    name: str
    slug: str
    deleted_at: datetime | None

    def is_deleted(self) -> bool:
        return self.deleted_at is not None


@dataclass(frozen=True, slots=True, kw_only=True)
class Tags(ValuedDataclass[Tag]):
    def all_tags_exist_by_ids(self, ids: set[IntId]) -> bool:
        return ids.difference({tag.id for tag in self.values}) == set()


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteTags(ValuedDataclass[Tag]): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class Note:
    id: UUID
    title: str
    content: str
    slug: str
    folder: str
    author_username: str
    published_at: datetime | None
    publish_status: PublishStatusEnum
    created_at: datetime
    updated_at: datetime
    tags: NoteTags

    def is_available(self) -> bool:
        return self.publish_status == PublishStatusEnum.PUBLISHED

    def public_copy(self) -> Note:
        return Note(
            id=self.id,
            title=self.title,
            content=self.content,
            slug=self.slug,
            folder=self.folder,
            author_username=self.author_username,
            published_at=self.published_at,
            publish_status=self.publish_status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            tags=NoteTags(values=[tag for tag in self.tags if not tag.is_deleted()]),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteList:
    total_count: int
    total_pages: int
    notes: list[Note]


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteFilters:
    page: int
    page_size: int
    only_published: bool
    tag_slug: str | None

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteCreateParams:
    id: UUID
    title: str
    content: str
    slug: str
    folder: str
    author_username: str
    publish_status: PublishStatusEnum
    tag_ids: list[IntId]


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteUpdateParams:
    title: str
    content: str
    slug: str
    folder: str
    publish_status: PublishStatusEnum
    tag_ids: list[IntId]


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteTreeItem:
    title: str
    slug: str
    publish_status: PublishStatusEnum
    published_at: datetime | None
    updated_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteTreeFolder:
    folder: str
    notes: list[NoteTreeItem]


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteTree:
    folders: list[NoteTreeFolder]


@dataclass(frozen=True, slots=True, kw_only=True)
class TagCreateParams:
    id: IntId
    name: str
    slug: str

    def to_tag(self) -> Tag:
        return Tag(id=self.id, name=self.name, slug=self.slug, deleted_at=None)


@dataclass(frozen=True, slots=True, kw_only=True)
class TagUpdateParams:
    name: str
    slug: str

    def to_tag(self, tag_id: IntId) -> Tag:
        return Tag(id=tag_id, name=self.name, slug=self.slug, deleted_at=None)
