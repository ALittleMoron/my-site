from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import date, datetime
from math import ceil
from typing import Self
from uuid import UUID

from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from core.schemas import ValuedDataclass
from core.types import IntId


@dataclass(frozen=True, slots=True, kw_only=True)
class Tag:
    id: IntId
    name_ru: str
    name_en: str
    slug: str
    deleted_at: datetime | None

    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def localized_name(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.name_ru
        return self.name_en


@dataclass(frozen=True, slots=True, kw_only=True)
class Tags(ValuedDataclass[Tag]):
    def all_tags_exist_by_ids(self, ids: set[IntId]) -> bool:
        return ids.difference({tag.id for tag in self.values}) == set()


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteMetadata:
    seo_title_ru: str | None
    seo_title_en: str | None
    seo_description_ru: str | None
    seo_description_en: str | None
    cover_image_url: str | None
    cover_image_alt_ru: str | None
    cover_image_alt_en: str | None

    def localized_seo_title(self, *, language: LanguageEnum) -> str | None:
        if language == LanguageEnum.RU:
            return self.seo_title_ru
        return self.seo_title_en

    def localized_seo_description(self, *, language: LanguageEnum) -> str | None:
        if language == LanguageEnum.RU:
            return self.seo_description_ru
        return self.seo_description_en

    def localized_cover_image_alt(self, *, language: LanguageEnum) -> str | None:
        if language == LanguageEnum.RU:
            return self.cover_image_alt_ru
        return self.cover_image_alt_en


@dataclass(frozen=True, slots=True, kw_only=True)
class Note:
    id: UUID
    slug: str
    title_ru: str
    title_en: str
    content_ru: str
    content_en: str
    folder_ru: str
    folder_en: str
    author_username: str
    published_at: datetime | None
    publish_status: PublishStatusEnum
    metadata: NoteMetadata
    created_at: datetime
    updated_at: datetime
    tags: Tags

    def is_available(self) -> bool:
        return self.publish_status == PublishStatusEnum.PUBLISHED

    def localized_title(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.title_ru
        return self.title_en

    def localized_content(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.content_ru
        return self.content_en

    def localized_folder(self, *, language: LanguageEnum) -> str:
        if language == LanguageEnum.RU:
            return self.folder_ru
        return self.folder_en

    def public_copy(self) -> Note:
        return replace(self, tags=Tags(values=[tag for tag in self.tags if not tag.is_deleted()]))


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishedNoteForSeo:
    slug: str
    publish_status: PublishStatusEnum
    updated_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishedNotesForSeo(ValuedDataclass[PublishedNoteForSeo]):
    @classmethod
    def from_notes(cls, *, notes: list[Note]) -> Self:
        return cls(
            values=[
                PublishedNoteForSeo(
                    slug=note.slug,
                    publish_status=note.publish_status,
                    updated_at=note.updated_at,
                )
                for note in notes
            ],
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class Notes(ValuedDataclass[Note]):
    total_count: int
    total_pages: int

    @classmethod
    def from_page(cls, *, values: list[Note], total_count: int, page_size: int) -> Self:
        return cls(
            values=values,
            total_count=total_count,
            total_pages=ceil(total_count / page_size) if total_count > 0 else 0,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteFilters:
    page: int | None = None
    page_size: int | None = None
    language: LanguageEnum = LanguageEnum.EN
    only_published: bool | None = None
    tag_slug: str | None = None
    published_from: date | None = None
    published_to: date | None = None
    search_query: str | None = None
    include_tags: bool = True
    order_for_seo: bool = False

    @property
    def limit(self) -> int:
        if self.page_size is None:
            raise ValueError
        return self.page_size

    @property
    def offset(self) -> int:
        if self.page is None or self.page_size is None:
            raise ValueError
        return (self.page - 1) * self.page_size


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteCreateParams:
    id: UUID
    slug: str
    title_ru: str
    title_en: str
    content_ru: str
    content_en: str
    folder_ru: str
    folder_en: str
    author_username: str
    publish_status: PublishStatusEnum
    metadata: NoteMetadata
    tag_ids: list[IntId]

    def to_note(self, *, now: datetime, tags: Tags) -> Note:
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
            publish_status=self.publish_status,
            metadata=self.metadata,
            published_at=now if self.publish_status == PublishStatusEnum.PUBLISHED else None,
            created_at=now,
            updated_at=now,
            tags=tags,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteUpdateParams:
    slug: str
    title_ru: str
    title_en: str
    content_ru: str
    content_en: str
    folder_ru: str
    folder_en: str
    publish_status: PublishStatusEnum
    metadata: NoteMetadata
    tag_ids: list[IntId]

    def to_note(self, *, existing_note: Note, now: datetime, tags: Tags) -> Note:
        published_at = existing_note.published_at
        if published_at is None and self.publish_status == PublishStatusEnum.PUBLISHED:
            published_at = now
        return Note(
            id=existing_note.id,
            slug=self.slug,
            title_ru=self.title_ru,
            title_en=self.title_en,
            content_ru=self.content_ru,
            content_en=self.content_en,
            folder_ru=self.folder_ru,
            folder_en=self.folder_en,
            author_username=existing_note.author_username,
            publish_status=self.publish_status,
            metadata=self.metadata,
            published_at=published_at,
            created_at=existing_note.created_at,
            updated_at=now,
            tags=tags,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteTreeItem:
    title: str
    slug: str
    publish_status: PublishStatusEnum
    published_at: datetime | None
    updated_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteTreeItemData:
    folder: str
    title: str
    slug: str
    publish_status: PublishStatusEnum
    published_at: datetime | None
    updated_at: datetime

    def to_tree_item(self) -> NoteTreeItem:
        return NoteTreeItem(
            title=self.title,
            slug=self.slug,
            publish_status=self.publish_status,
            published_at=self.published_at,
            updated_at=self.updated_at,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteTreeFolder:
    folder: str
    notes: list[NoteTreeItem]


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteTree:
    folders: list[NoteTreeFolder]

    @classmethod
    def from_items(cls, *, items: list[NoteTreeItemData]) -> Self:
        folders: defaultdict[str, list[NoteTreeItem]] = defaultdict(list)
        for item in items:
            folders[item.folder].append(item.to_tree_item())
        return cls(
            folders=[
                NoteTreeFolder(folder=folder, notes=notes)
                for folder, notes in sorted(folders.items(), key=lambda item: item[0].lower())
            ],
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteReactionCounts:
    heart: int
    fire: int
    thinking: int
    neutral: int
    poop: int

    @classmethod
    def zero(cls) -> Self:
        return cls(heart=0, fire=0, thinking=0, neutral=0, poop=0)

    @classmethod
    def from_counts(cls, *, counts: Mapping[NoteReactionKind, int]) -> Self:
        return cls(
            heart=counts.get(NoteReactionKind.HEART, 0),
            fire=counts.get(NoteReactionKind.FIRE, 0),
            thinking=counts.get(NoteReactionKind.THINKING, 0),
            neutral=counts.get(NoteReactionKind.NEUTRAL, 0),
            poop=counts.get(NoteReactionKind.POOP, 0),
        )

    @property
    def total(self) -> int:
        return self.heart + self.fire + self.thinking + self.neutral + self.poop


@dataclass(frozen=True, slots=True, kw_only=True)
class NotePublicStats:
    note_id: UUID
    view_count: int
    reaction_counts: NoteReactionCounts


@dataclass(frozen=True, slots=True, kw_only=True)
class NotePublicStatsCollection(ValuedDataclass[NotePublicStats]):
    def by_note_id(self, note_id: UUID) -> NotePublicStats:
        for stats in self.values:
            if stats.note_id == note_id:
                return stats
        return NotePublicStats(
            note_id=note_id,
            view_count=0,
            reaction_counts=NoteReactionCounts.zero(),
        )

    def fill_missing(self, note_ids: list[UUID]) -> NotePublicStatsCollection:
        return NotePublicStatsCollection(values=[self.by_note_id(note_id) for note_id in note_ids])


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteAnalyticsTotals:
    view_count: int
    engaged_view_count: int
    reaction_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteAnalyticsNoteStats:
    note_id: UUID
    title: str
    slug: str
    view_count: int
    engaged_view_count: int
    reaction_counts: NoteReactionCounts

    @classmethod
    def from_daily_stats(
        cls,
        *,
        daily: NoteAnalyticsDailyStats,
        reaction_counts: NoteReactionCounts,
    ) -> Self:
        return cls(
            note_id=daily.note_id,
            title=daily.title,
            slug=daily.slug,
            view_count=daily.view_count,
            engaged_view_count=daily.engaged_view_count,
            reaction_counts=reaction_counts,
        )

    def with_daily_stats(self, *, daily: NoteAnalyticsDailyStats) -> Self:
        return self.__class__(
            note_id=self.note_id,
            title=self.title,
            slug=self.slug,
            view_count=self.view_count + daily.view_count,
            engaged_view_count=self.engaged_view_count + daily.engaged_view_count,
            reaction_counts=self.reaction_counts,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteAnalyticsDailyStats:
    note_id: UUID
    title: str
    slug: str
    date: date
    source_category: NoteViewSourceCategory
    view_count: int
    engaged_view_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteAnalyticsStats:
    date_from: date
    date_to: date
    totals: NoteAnalyticsTotals
    notes: list[NoteAnalyticsNoteStats]
    daily: list[NoteAnalyticsDailyStats]

    @classmethod
    def from_daily_stats(
        cls,
        *,
        date_from: date,
        date_to: date,
        daily: list[NoteAnalyticsDailyStats],
        reaction_counts: dict[UUID, NoteReactionCounts],
    ) -> Self:
        notes = cls._build_note_stats(daily=daily, reaction_counts=reaction_counts)
        return cls(
            date_from=date_from,
            date_to=date_to,
            totals=NoteAnalyticsTotals(
                view_count=sum(item.view_count for item in daily),
                engaged_view_count=sum(item.engaged_view_count for item in daily),
                reaction_count=sum(item.reaction_counts.total for item in notes),
            ),
            notes=notes,
            daily=daily,
        )

    @classmethod
    def _build_note_stats(
        cls,
        *,
        daily: list[NoteAnalyticsDailyStats],
        reaction_counts: dict[UUID, NoteReactionCounts],
    ) -> list[NoteAnalyticsNoteStats]:
        note_stats: dict[UUID, NoteAnalyticsNoteStats] = {}
        for item in daily:
            existing = note_stats.get(item.note_id)
            if existing is None:
                note_stats[item.note_id] = NoteAnalyticsNoteStats.from_daily_stats(
                    daily=item,
                    reaction_counts=reaction_counts.get(item.note_id, NoteReactionCounts.zero()),
                )
            else:
                note_stats[item.note_id] = existing.with_daily_stats(daily=item)
        return sorted(note_stats.values(), key=lambda item: (-item.view_count, item.title))


@dataclass(frozen=True, slots=True, kw_only=True)
class TagCreateParams:
    id: IntId
    name_ru: str
    name_en: str
    slug: str

    def to_tag(self) -> Tag:
        return Tag(
            id=self.id,
            name_ru=self.name_ru,
            name_en=self.name_en,
            slug=self.slug,
            deleted_at=None,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class TagUpdateParams:
    name_ru: str
    name_en: str
    slug: str

    def to_tag(self, tag_id: IntId) -> Tag:
        return Tag(
            id=tag_id,
            name_ru=self.name_ru,
            name_en=self.name_en,
            slug=self.slug,
            deleted_at=None,
        )
