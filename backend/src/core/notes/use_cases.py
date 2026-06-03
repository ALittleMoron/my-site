import hmac
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, date, datetime
from hashlib import sha256
from urllib.parse import urlparse
from uuid import UUID

from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from core.notes.event_dispatchers import NoteAnalyticsErrorReporter
from core.notes.exceptions import NoteNotFoundError, TagNotFoundError
from core.notes.schemas import (
    Note,
    NoteAnalyticsStats,
    NoteCreateParams,
    NoteFilters,
    NotePublicStatsCollection,
    Notes,
    NoteTree,
    NoteUpdateParams,
    PublishedNoteForSeo,
    Tag,
    TagCreateParams,
    Tags,
    TagUpdateParams,
)
from core.notes.storages import NoteAnalyticsStorage, NotesStorage
from core.schemas import Secret
from core.types import IntId


class AbstractNotesUseCase(ABC):
    @abstractmethod
    async def get_note(self, *, slug: str, only_published: bool) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def list_notes(self, *, filters: NoteFilters) -> Notes:
        raise NotImplementedError

    @abstractmethod
    async def list_published_notes_for_seo(self) -> list[PublishedNoteForSeo]:
        raise NotImplementedError

    @abstractmethod
    async def list_tree(self, *, only_published: bool, language: LanguageEnum) -> NoteTree:
        raise NotImplementedError

    @abstractmethod
    async def create_note(self, *, params: NoteCreateParams) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def update_note(
        self,
        *,
        slug: str,
        params: NoteUpdateParams,
    ) -> Note:
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
    async def create_tag(self, *, params: TagCreateParams) -> Tag:
        raise NotImplementedError

    @abstractmethod
    async def update_tag(
        self,
        *,
        tag_id: IntId,
        params: TagUpdateParams,
    ) -> Tag:
        raise NotImplementedError

    @abstractmethod
    async def soft_delete_tag(self, *, tag_id: IntId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def restore_tag(self, *, tag_id: IntId) -> None:
        raise NotImplementedError


class AbstractNoteAnalyticsUseCase(ABC):
    @abstractmethod
    async def track_public_view(
        self,
        *,
        note: Note,
        referrer: str | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def track_view(
        self,
        *,
        note: Note,
        source_category: NoteViewSourceCategory,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def track_engaged_view(
        self,
        *,
        slug: str,
        source_category: NoteViewSourceCategory,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_public_stats(self, *, note_ids: list[UUID]) -> NotePublicStatsCollection:
        raise NotImplementedError

    @abstractmethod
    async def set_reaction(
        self,
        *,
        slug: str,
        client_token: str,
        reaction_kind: NoteReactionKind | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_stats(
        self,
        *,
        date_from: date,
        date_to: date,
        language: LanguageEnum,
    ) -> NoteAnalyticsStats:
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

    async def list_notes(self, *, filters: NoteFilters) -> Notes:
        notes, total_count = await self.storage.list_notes(filters=filters)
        return Notes.from_page(
            values=notes,
            total_count=total_count,
            page_size=filters.page_size,
        )

    async def list_published_notes_for_seo(self) -> list[PublishedNoteForSeo]:
        return await self.storage.list_published_notes_for_seo()

    async def list_tree(self, *, only_published: bool, language: LanguageEnum) -> NoteTree:
        items = await self.storage.list_tree_items(
            only_published=only_published,
            language=language,
        )
        return NoteTree.from_items(items=items)

    async def create_note(self, *, params: NoteCreateParams) -> Note:
        tags = await self._get_active_tags(tag_ids=params.tag_ids)
        now = datetime.now(tz=UTC)
        return await self.storage.create_note(note=params.to_note(now=now, tags=tags))

    async def update_note(
        self,
        *,
        slug: str,
        params: NoteUpdateParams,
    ) -> Note:
        existing_note = await self.storage.get_note_by_slug(
            slug=slug,
            include_deleted_tags=True,
        )
        tags = await self._get_active_tags(tag_ids=params.tag_ids)
        now = datetime.now(tz=UTC)
        return await self.storage.update_note(
            note=params.to_note(existing_note=existing_note, now=now, tags=tags),
        )

    async def _get_active_tags(self, *, tag_ids: list[IntId]) -> Tags:
        tags = await self.storage.get_tags_by_ids(
            tag_ids=tag_ids,
            include_deleted=False,
        )
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

    async def list_tags(self, *, include_deleted: bool, language: LanguageEnum) -> Tags:
        return await self.storage.list_tags(include_deleted=include_deleted, language=language)

    async def search_tags(
        self,
        *,
        search_name: str,
        include_deleted: bool,
        limit: int,
        language: LanguageEnum,
    ) -> Tags:
        return await self.storage.search_tags(
            search_name=search_name,
            include_deleted=include_deleted,
            limit=limit,
            language=language,
        )

    async def create_tag(self, *, params: TagCreateParams) -> Tag:
        return await self.storage.create_tag(tag=params.to_tag())

    async def update_tag(
        self,
        *,
        tag_id: IntId,
        params: TagUpdateParams,
    ) -> Tag:
        return await self.storage.update_tag(tag=params.to_tag(tag_id=tag_id))

    async def soft_delete_tag(self, *, tag_id: IntId) -> None:
        await self.storage.soft_delete_tag(tag_id=tag_id)

    async def restore_tag(self, *, tag_id: IntId) -> None:
        await self.storage.restore_tag(tag_id=tag_id)


@dataclass(kw_only=True, slots=True, frozen=True)
class NoteAnalyticsUseCase(AbstractNoteAnalyticsUseCase):
    notes_storage: NotesStorage
    analytics_storage: NoteAnalyticsStorage
    reaction_secret: Secret[str]
    app_domain: str
    error_reporter: NoteAnalyticsErrorReporter

    async def track_public_view(
        self,
        *,
        note: Note,
        referrer: str | None,
    ) -> None:
        try:
            await self.track_view(
                note=note,
                source_category=self._classify_source_category(referrer=referrer),
            )
        except Exception as exc:  # noqa: BLE001
            self.error_reporter.report_public_view_tracking_failure(note=note, error=exc)

    async def track_view(
        self,
        *,
        note: Note,
        source_category: NoteViewSourceCategory,
    ) -> None:
        if not note.is_available():
            return
        await self.analytics_storage.increment_view(
            note_id=note.id,
            source_category=source_category,
            viewed_on=None,
        )

    async def track_engaged_view(
        self,
        *,
        slug: str,
        source_category: NoteViewSourceCategory,
    ) -> None:
        note = await self._get_published_note(slug=slug)
        await self.analytics_storage.increment_engaged_view(
            note_id=note.id,
            source_category=source_category,
            viewed_on=None,
        )

    async def get_public_stats(self, *, note_ids: list[UUID]) -> NotePublicStatsCollection:
        unique_note_ids = list(dict.fromkeys(note_ids))
        stats = await self.analytics_storage.get_public_stats(note_ids=unique_note_ids)
        return stats.fill_missing(note_ids=unique_note_ids)

    async def set_reaction(
        self,
        *,
        slug: str,
        client_token: str,
        reaction_kind: NoteReactionKind | None,
    ) -> None:
        note = await self._get_published_note(slug=slug)
        await self.analytics_storage.set_reaction(
            note_id=note.id,
            note_scoped_voter_hash=self._build_note_scoped_voter_hash(
                note_id=note.id,
                client_token=client_token,
            ),
            reaction_kind=reaction_kind,
        )

    async def get_stats(
        self,
        *,
        date_from: date,
        date_to: date,
        language: LanguageEnum,
    ) -> NoteAnalyticsStats:
        daily = await self.analytics_storage.get_daily_stats(
            date_from=date_from,
            date_to=date_to,
            language=language,
        )
        note_ids = list(dict.fromkeys(item.note_id for item in daily))
        reaction_counts = await self.analytics_storage.get_reaction_counts(note_ids=note_ids)
        return NoteAnalyticsStats.from_daily_stats(
            date_from=date_from,
            date_to=date_to,
            daily=daily,
            reaction_counts=reaction_counts,
        )

    async def _get_published_note(self, *, slug: str) -> Note:
        note = await self.notes_storage.get_note_by_slug(
            slug=slug,
            include_deleted_tags=False,
        )
        if not note.is_available():
            raise NoteNotFoundError
        return note

    def _classify_source_category(self, *, referrer: str | None) -> NoteViewSourceCategory:
        if not referrer:
            return NoteViewSourceCategory.DIRECT
        hostname = urlparse(referrer).hostname
        if hostname is None:
            return NoteViewSourceCategory.UNKNOWN
        normalized_hostname = hostname.lower()
        app_domain = self.app_domain.lower()
        if normalized_hostname == app_domain or normalized_hostname.endswith(f".{app_domain}"):
            return NoteViewSourceCategory.INTERNAL
        if self._is_search_hostname(hostname=normalized_hostname):
            return NoteViewSourceCategory.SEARCH
        if self._is_social_hostname(hostname=normalized_hostname):
            return NoteViewSourceCategory.SOCIAL
        return NoteViewSourceCategory.EXTERNAL

    def _is_search_hostname(self, *, hostname: str) -> bool:
        return any(
            search_hostname in hostname
            for search_hostname in (
                "google.",
                "yandex.",
                "bing.",
                "duckduckgo.",
                "search.yahoo.",
            )
        )

    def _is_social_hostname(self, *, hostname: str) -> bool:
        return any(
            social_hostname in hostname
            for social_hostname in (
                "facebook.",
                "linkedin.",
                "reddit.",
                "t.me",
                "telegram.",
                "twitter.",
                "x.com",
                "vk.",
            )
        )

    def _build_note_scoped_voter_hash(self, *, note_id: UUID, client_token: str) -> str:
        message = f"{note_id}:{client_token}".encode()
        return hmac.new(
            self.reaction_secret.get_secret_value().encode(),
            message,
            sha256,
        ).hexdigest()
