from abc import ABC, abstractmethod

from core.enums import PublishStatusEnum
from core.notes.schemas import Note, NoteFilters, NoteList, NoteTree, Tag, Tags
from core.types import IntId


class NotesStorage(ABC):
    @abstractmethod
    async def get_note_by_slug(self, *, slug: str, include_deleted_tags: bool) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def list_notes(self, *, filters: NoteFilters) -> NoteList:
        raise NotImplementedError

    @abstractmethod
    async def list_tree(self, *, only_published: bool) -> NoteTree:
        raise NotImplementedError

    @abstractmethod
    async def create_note(self, *, note: Note) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def update_note(self, *, note: Note) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def delete_note(self, *, slug: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_note_publish_status(
        self,
        *,
        slug: str,
        publish_status: PublishStatusEnum,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_tags_by_ids(self, *, tag_ids: list[IntId], include_deleted: bool) -> Tags:
        raise NotImplementedError

    @abstractmethod
    async def list_tags(self, *, include_deleted: bool) -> Tags:
        raise NotImplementedError

    @abstractmethod
    async def search_tags(self, *, search_name: str, include_deleted: bool, limit: int) -> Tags:
        raise NotImplementedError

    @abstractmethod
    async def create_tag(self, *, tag: Tag) -> Tag:
        raise NotImplementedError

    @abstractmethod
    async def update_tag(self, *, tag: Tag) -> Tag:
        raise NotImplementedError

    @abstractmethod
    async def soft_delete_tag(self, *, tag_id: IntId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def restore_tag(self, *, tag_id: IntId) -> None:
        raise NotImplementedError
