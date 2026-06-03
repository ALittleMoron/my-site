from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from core.notes.schemas import (
    Note,
    NoteAnalyticsDailyStats,
    NoteFilters,
    NotePublicStatsCollection,
    NoteReactionCounts,
    NoteTreeItemData,
    PublishedNoteForSeo,
    Tag,
    Tags,
)
from core.types import IntId


class NotesStorage(ABC):
    @abstractmethod
    async def get_note_by_slug(
        self,
        *,
        slug: str,
        include_deleted_tags: bool,
    ) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def list_notes(self, *, filters: NoteFilters) -> tuple[list[Note], int]:
        raise NotImplementedError

    @abstractmethod
    async def list_published_notes_for_seo(self) -> list[PublishedNoteForSeo]:
        raise NotImplementedError

    @abstractmethod
    async def list_tree_items(
        self,
        *,
        only_published: bool,
        language: LanguageEnum,
    ) -> list[NoteTreeItemData]:
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
    async def get_tags_by_ids(
        self,
        *,
        tag_ids: list[IntId],
        include_deleted: bool,
    ) -> Tags:
        raise NotImplementedError

    @abstractmethod
    async def list_tags(self, *, include_deleted: bool, language: LanguageEnum) -> Tags:
        raise NotImplementedError

    @abstractmethod
    async def search_tags(
        self,
        *,
        search_name: str,
        include_deleted: bool,
        limit: int,
        language: LanguageEnum,
    ) -> Tags:
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


class NoteAnalyticsStorage(ABC):
    @abstractmethod
    async def increment_view(
        self,
        *,
        note_id: UUID,
        source_category: NoteViewSourceCategory,
        viewed_on: date | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def increment_engaged_view(
        self,
        *,
        note_id: UUID,
        source_category: NoteViewSourceCategory,
        viewed_on: date | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_public_stats(self, *, note_ids: list[UUID]) -> NotePublicStatsCollection:
        raise NotImplementedError

    @abstractmethod
    async def set_reaction(
        self,
        *,
        note_id: UUID,
        note_scoped_voter_hash: str,
        reaction_kind: NoteReactionKind | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_daily_stats(
        self,
        *,
        date_from: date,
        date_to: date,
        language: LanguageEnum,
    ) -> list[NoteAnalyticsDailyStats]:
        raise NotImplementedError

    @abstractmethod
    async def get_reaction_counts(self, *, note_ids: list[UUID]) -> dict[UUID, NoteReactionCounts]:
        raise NotImplementedError
