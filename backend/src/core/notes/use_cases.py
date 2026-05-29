from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime

from core.enums import PublishStatusEnum
from core.notes.exceptions import NoteNotFoundError, TagNotFoundError
from core.notes.schemas import (
    Note,
    NoteCreateParams,
    NoteFilters,
    NoteList,
    NoteTags,
    NoteTree,
    NoteUpdateParams,
    Tag,
    TagCreateParams,
    Tags,
    TagUpdateParams,
)
from core.notes.storages import NotesStorage
from core.types import IntId


class AbstractNotesUseCase(ABC):
    @abstractmethod
    async def get_note(self, *, slug: str, only_published: bool) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def list_notes(self, *, filters: NoteFilters) -> NoteList:
        raise NotImplementedError

    @abstractmethod
    async def list_tree(self, *, only_published: bool) -> NoteTree:
        raise NotImplementedError

    @abstractmethod
    async def create_note(self, *, params: NoteCreateParams) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def update_note(self, *, slug: str, params: NoteUpdateParams) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def delete_note(self, *, slug: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def switch_note_publish_status(
        self,
        *,
        slug: str,
        publish_status: PublishStatusEnum,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_tags(self, *, include_deleted: bool) -> Tags:
        raise NotImplementedError

    @abstractmethod
    async def search_tags(self, *, search_name: str, include_deleted: bool, limit: int) -> Tags:
        raise NotImplementedError

    @abstractmethod
    async def create_tag(self, *, params: TagCreateParams) -> Tag:
        raise NotImplementedError

    @abstractmethod
    async def update_tag(self, *, tag_id: IntId, params: TagUpdateParams) -> Tag:
        raise NotImplementedError

    @abstractmethod
    async def soft_delete_tag(self, *, tag_id: IntId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def restore_tag(self, *, tag_id: IntId) -> None:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class NotesUseCase(AbstractNotesUseCase):
    storage: NotesStorage

    async def get_note(self, *, slug: str, only_published: bool) -> Note:
        note = await self.storage.get_note_by_slug(
            slug=slug,
            include_deleted_tags=not only_published,
        )
        if only_published and not note.is_available():
            raise NoteNotFoundError
        return note.public_copy() if only_published else note

    async def list_notes(self, *, filters: NoteFilters) -> NoteList:
        return await self.storage.list_notes(filters=filters)

    async def list_tree(self, *, only_published: bool) -> NoteTree:
        return await self.storage.list_tree(only_published=only_published)

    async def create_note(self, *, params: NoteCreateParams) -> Note:
        tags = await self._get_active_tags(tag_ids=params.tag_ids)
        now = datetime.now(tz=UTC)
        note = Note(
            id=params.id,
            title=params.title,
            content=params.content,
            slug=params.slug,
            folder=params.folder,
            author_username=params.author_username,
            publish_status=params.publish_status,
            published_at=now if params.publish_status == PublishStatusEnum.PUBLISHED else None,
            created_at=now,
            updated_at=now,
            tags=NoteTags(values=tags.values),
        )
        return await self.storage.create_note(note=note)

    async def update_note(self, *, slug: str, params: NoteUpdateParams) -> Note:
        existing_note = await self.storage.get_note_by_slug(slug=slug, include_deleted_tags=True)
        tags = await self._get_active_tags(tag_ids=params.tag_ids)
        now = datetime.now(tz=UTC)
        published_at = existing_note.published_at
        if published_at is None and params.publish_status == PublishStatusEnum.PUBLISHED:
            published_at = now
        note = Note(
            id=existing_note.id,
            title=params.title,
            content=params.content,
            slug=params.slug,
            folder=params.folder,
            author_username=existing_note.author_username,
            publish_status=params.publish_status,
            published_at=published_at,
            created_at=existing_note.created_at,
            updated_at=now,
            tags=NoteTags(values=tags.values),
        )
        return await self.storage.update_note(note=note)

    async def _get_active_tags(self, *, tag_ids: list[IntId]) -> Tags:
        tags = await self.storage.get_tags_by_ids(tag_ids=tag_ids, include_deleted=False)
        if not tags.all_tags_exist_by_ids(ids=set(tag_ids)):
            raise TagNotFoundError
        return tags

    async def delete_note(self, *, slug: str) -> None:
        await self.storage.delete_note(slug=slug)

    async def switch_note_publish_status(
        self,
        *,
        slug: str,
        publish_status: PublishStatusEnum,
    ) -> None:
        await self.storage.update_note_publish_status(slug=slug, publish_status=publish_status)

    async def list_tags(self, *, include_deleted: bool) -> Tags:
        return await self.storage.list_tags(include_deleted=include_deleted)

    async def search_tags(self, *, search_name: str, include_deleted: bool, limit: int) -> Tags:
        return await self.storage.search_tags(
            search_name=search_name,
            include_deleted=include_deleted,
            limit=limit,
        )

    async def create_tag(self, *, params: TagCreateParams) -> Tag:
        return await self.storage.create_tag(tag=params.to_tag())

    async def update_tag(self, *, tag_id: IntId, params: TagUpdateParams) -> Tag:
        return await self.storage.update_tag(tag=params.to_tag(tag_id=tag_id))

    async def soft_delete_tag(self, *, tag_id: IntId) -> None:
        await self.storage.soft_delete_tag(tag_id=tag_id)

    async def restore_tag(self, *, tag_id: IntId) -> None:
        await self.storage.restore_tag(tag_id=tag_id)
