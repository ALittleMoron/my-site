from dataclasses import dataclass
from datetime import UTC, date, datetime
from math import ceil
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import Select, case, func, or_, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.enums import PublishStatusEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from core.notes.exceptions import NoteNotFoundError, TagNotFoundError
from core.notes.schemas import (
    Note,
    NoteAnalyticsDailyStats,
    NoteAnalyticsNoteStats,
    NoteAnalyticsStats,
    NoteAnalyticsTotals,
    NoteFilters,
    NotePublicStats,
    NotePublicStatsCollection,
    NoteReactionCounts,
    Notes,
    NoteTree,
    NoteTreeFolder,
    NoteTreeItem,
    Tag,
    Tags,
)
from core.notes.storages import NoteAnalyticsStorage, NotesStorage
from core.types import IntId
from infra.postgresql.models import (
    NoteDailyAnalyticsModel,
    NoteModel,
    NoteReactionModel,
    NoteToTagSecondaryModel,
    TagModel,
)

_SelectT = TypeVar("_SelectT")


@dataclass(kw_only=True)
class NotesDatabaseStorage(NotesStorage):
    session: AsyncSession

    async def get_note_by_slug(self, *, slug: str, include_deleted_tags: bool) -> Note:
        query = (
            select(NoteModel)
            .where(NoteModel.slug == slug)
            .options(
                selectinload(NoteModel.tag_links).selectinload(NoteToTagSecondaryModel.tag),
            )
        )
        note_model = await self.session.scalar(query)
        if note_model is None:
            raise NoteNotFoundError
        return note_model.to_domain_schema(include_deleted_tags=include_deleted_tags)

    async def list_notes(self, *, filters: NoteFilters) -> Notes:
        query = self._apply_note_filters(
            select(NoteModel).options(
                selectinload(NoteModel.tag_links).selectinload(NoteToTagSecondaryModel.tag),
            ),
            filters=filters,
        )
        query = query.order_by(*self._note_ordering()).offset(filters.offset).limit(filters.limit)
        count_query = self._apply_note_filters(
            select(func.count(func.distinct(NoteModel.id))),
            filters=filters,
        )
        total_count = (await self.session.scalar(count_query)) or 0

        note_models = await self.session.scalars(query)

        return Notes(
            values=[
                note_model.to_domain_schema(include_deleted_tags=not filters.only_published)
                for note_model in note_models.unique()
            ],
            total_count=total_count,
            total_pages=ceil(total_count / filters.page_size) if total_count > 0 else 0,
        )

    def _apply_note_filters(
        self,
        query: Select[tuple[_SelectT]],
        *,
        filters: NoteFilters,
    ) -> Select[tuple[_SelectT]]:
        if filters.only_published:
            query = query.where(NoteModel.publish_status == PublishStatusEnum.PUBLISHED)
        if filters.tag_slug is not None:
            query = (
                query.join(NoteModel.tag_links)
                .join(NoteToTagSecondaryModel.tag)
                .where(TagModel.slug == filters.tag_slug, TagModel.deleted_at.is_(None))
            )
        return query

    def _note_ordering(self) -> tuple[Any, ...]:
        return (
            case((NoteModel.publish_status == PublishStatusEnum.PUBLISHED, 0), else_=1),
            NoteModel.published_at.desc().nullslast(),
            NoteModel.updated_at.desc(),
            NoteModel.title,
        )

    async def list_tree(self, *, only_published: bool) -> NoteTree:
        query = select(NoteModel).order_by(NoteModel.folder, *self._note_ordering())
        if only_published:
            query = query.where(NoteModel.publish_status == PublishStatusEnum.PUBLISHED)
        models = await self.session.scalars(query)
        folders: dict[str, list[NoteTreeItem]] = {}
        for model in models:
            folders.setdefault(model.folder, []).append(
                NoteTreeItem(
                    title=model.title,
                    slug=model.slug,
                    publish_status=model.publish_status,
                    published_at=model.published_at,
                    updated_at=model.updated_at,
                ),
            )
        return NoteTree(
            folders=[
                NoteTreeFolder(folder=folder, notes=notes)
                for folder, notes in sorted(folders.items(), key=lambda item: item[0].lower())
            ],
        )

    async def create_note(self, *, note: Note) -> Note:
        model = NoteModel.from_domain_schema(note=note)
        model.tag_links = self._build_tag_links(note=note)
        self.session.add(model)
        await self.session.flush()
        return await self.get_note_by_slug(slug=note.slug, include_deleted_tags=True)

    async def update_note(self, *, note: Note) -> Note:
        query = (
            select(NoteModel)
            .where(NoteModel.id == note.id)
            .options(selectinload(NoteModel.tag_links))
        )
        model = await self.session.scalar(query)
        if model is None:
            raise NoteNotFoundError
        model.update_from_domain_schema(note=note)
        model.tag_links = self._build_tag_links(note=note)
        await self.session.flush()
        return await self.get_note_by_slug(slug=note.slug, include_deleted_tags=True)

    def _build_tag_links(self, *, note: Note) -> list[NoteToTagSecondaryModel]:
        return [NoteToTagSecondaryModel.from_domain_schema(tag=tag) for tag in note.tags]

    async def _get_note_model(self, *, slug: str, load_tag_links: bool) -> NoteModel:
        query = select(NoteModel).where(NoteModel.slug == slug)
        if load_tag_links:
            query = query.options(selectinload(NoteModel.tag_links))
        model = await self.session.scalar(query)
        if model is None:
            raise NoteNotFoundError
        return model

    async def delete_note(self, *, slug: str) -> None:
        model = await self._get_note_model(slug=slug, load_tag_links=False)
        await self.session.delete(model)
        await self.session.flush()

    async def update_note_publish_status(
        self,
        *,
        slug: str,
        publish_status: PublishStatusEnum,
    ) -> None:
        model = await self._get_note_model(slug=slug, load_tag_links=False)
        model.publish_status = publish_status
        if publish_status == PublishStatusEnum.PUBLISHED and model.published_at is None:
            model.published_at = datetime.now(tz=UTC)
        await self.session.flush()

    async def get_tags_by_ids(self, *, tag_ids: list[IntId], include_deleted: bool) -> Tags:
        if not tag_ids:
            return Tags(values=[])
        query = select(TagModel).where(TagModel.id.in_(tag_ids))
        if not include_deleted:
            query = query.where(TagModel.deleted_at.is_(None))
        models = await self.session.scalars(query)
        return Tags(values=[model.to_domain_schema() for model in models])

    async def list_tags(self, *, include_deleted: bool) -> Tags:
        query = select(TagModel).order_by(func.lower(TagModel.name), TagModel.id)
        if not include_deleted:
            query = query.where(TagModel.deleted_at.is_(None))
        models = await self.session.scalars(query)
        return Tags(values=[model.to_domain_schema() for model in models])

    async def search_tags(self, *, search_name: str, include_deleted: bool, limit: int) -> Tags:
        lowered_search_name = search_name.lower()
        query = (
            select(TagModel)
            .where(
                or_(
                    func.lower(TagModel.name).ilike(f"%{lowered_search_name}%"),
                    func.lower(TagModel.slug).ilike(f"%{lowered_search_name}%"),
                ),
            )
            .order_by(
                case(
                    (func.lower(TagModel.name) == lowered_search_name, 0),
                    (func.lower(TagModel.name).startswith(lowered_search_name), 1),
                    else_=2,
                ),
                TagModel.name,
            )
            .limit(limit)
        )
        if not include_deleted:
            query = query.where(TagModel.deleted_at.is_(None))
        models = await self.session.scalars(query)
        return Tags(values=[model.to_domain_schema() for model in models])

    async def create_tag(self, *, tag: Tag) -> Tag:
        model = TagModel.from_domain_schema(tag=tag)
        self.session.add(model)
        await self.session.flush()
        return model.to_domain_schema()

    async def update_tag(self, *, tag: Tag) -> Tag:
        model = await self._get_tag_model(tag_id=tag.id)
        model.update_from_domain_schema(tag=tag)
        await self.session.flush()
        return model.to_domain_schema()

    async def _get_tag_model(self, *, tag_id: IntId) -> TagModel:
        model = await self.session.scalar(select(TagModel).where(TagModel.id == tag_id))
        if model is None:
            raise TagNotFoundError
        return model

    async def soft_delete_tag(self, *, tag_id: IntId) -> None:
        model = await self._get_tag_model(tag_id=tag_id)
        if model.deleted_at is None:
            model.deleted_at = datetime.now(tz=UTC)
        await self.session.flush()

    async def restore_tag(self, *, tag_id: IntId) -> None:
        model = await self._get_tag_model(tag_id=tag_id)
        model.deleted_at = None
        await self.session.flush()


@dataclass(kw_only=True)
class NoteAnalyticsDatabaseStorage(NoteAnalyticsStorage):
    session: AsyncSession

    async def increment_view(
        self,
        *,
        note_id: UUID,
        source_category: NoteViewSourceCategory,
        viewed_on: date | None,
    ) -> None:
        await self._increment_daily_counter(
            note_id=note_id,
            source_category=source_category,
            viewed_on=viewed_on,
            view_count_increment=1,
            engaged_view_count_increment=0,
        )

    async def increment_engaged_view(
        self,
        *,
        note_id: UUID,
        source_category: NoteViewSourceCategory,
        viewed_on: date | None,
    ) -> None:
        await self._increment_daily_counter(
            note_id=note_id,
            source_category=source_category,
            viewed_on=viewed_on,
            view_count_increment=0,
            engaged_view_count_increment=1,
        )

    async def _increment_daily_counter(
        self,
        *,
        note_id: UUID,
        source_category: NoteViewSourceCategory,
        viewed_on: date | None,
        view_count_increment: int,
        engaged_view_count_increment: int,
    ) -> None:
        recorded_on = viewed_on if viewed_on is not None else datetime.now(tz=UTC).date()
        insert_statement = postgresql_insert(NoteDailyAnalyticsModel).values(
            note_id=note_id,
            date=recorded_on,
            source_category=source_category,
            view_count=view_count_increment,
            engaged_view_count=engaged_view_count_increment,
        )
        await self.session.execute(
            insert_statement.on_conflict_do_update(
                index_elements=[
                    NoteDailyAnalyticsModel.note_id,
                    NoteDailyAnalyticsModel.date,
                    NoteDailyAnalyticsModel.source_category,
                ],
                set_={
                    NoteDailyAnalyticsModel.view_count.key: (
                        NoteDailyAnalyticsModel.view_count + view_count_increment
                    ),
                    NoteDailyAnalyticsModel.engaged_view_count.key: (
                        NoteDailyAnalyticsModel.engaged_view_count + engaged_view_count_increment
                    ),
                },
            ),
        )
        await self.session.flush()

    async def get_public_stats(self, *, note_ids: list[UUID]) -> NotePublicStatsCollection:
        if not note_ids:
            return NotePublicStatsCollection(values=[])
        view_counts = await self._get_view_counts(note_ids=note_ids)
        reaction_counts = await self._get_reaction_counts(note_ids=note_ids)
        return NotePublicStatsCollection(
            values=[
                NotePublicStats(
                    note_id=note_id,
                    view_count=view_counts.get(note_id, 0),
                    reaction_counts=reaction_counts.get(note_id, NoteReactionCounts.zero()),
                )
                for note_id in note_ids
            ],
        )

    async def _get_view_counts(self, *, note_ids: list[UUID]) -> dict[UUID, int]:
        result = await self.session.execute(
            select(
                NoteDailyAnalyticsModel.note_id,
                func.coalesce(func.sum(NoteDailyAnalyticsModel.view_count), 0),
            )
            .where(NoteDailyAnalyticsModel.note_id.in_(note_ids))
            .group_by(NoteDailyAnalyticsModel.note_id),
        )
        return {row[0]: row[1] for row in result}

    async def _get_reaction_counts(self, *, note_ids: list[UUID]) -> dict[UUID, NoteReactionCounts]:
        result = await self.session.execute(
            select(
                NoteReactionModel.note_id,
                NoteReactionModel.reaction_kind,
                func.count(NoteReactionModel.id),
            )
            .where(NoteReactionModel.note_id.in_(note_ids))
            .group_by(NoteReactionModel.note_id, NoteReactionModel.reaction_kind),
        )
        raw_counts: dict[UUID, dict[NoteReactionKind, int]] = {}
        for note_id, reaction_kind, count in result:
            raw_counts.setdefault(note_id, {})[self._to_reaction_kind(reaction_kind)] = count
        return {
            note_id: self._build_reaction_counts(counts=counts)
            for note_id, counts in raw_counts.items()
        }

    async def set_reaction(
        self,
        *,
        note_id: UUID,
        note_scoped_voter_hash: str,
        reaction_kind: NoteReactionKind | None,
    ) -> None:
        model = await self.session.scalar(
            select(NoteReactionModel)
            .where(
                NoteReactionModel.note_id == note_id,
                NoteReactionModel.note_scoped_voter_hash == note_scoped_voter_hash,
            )
            .with_for_update(),
        )
        if reaction_kind is None:
            if model is not None:
                await self.session.delete(model)
            await self.session.flush()
            return
        if model is None:
            self.session.add(
                NoteReactionModel(
                    note_id=note_id,
                    note_scoped_voter_hash=note_scoped_voter_hash,
                    reaction_kind=reaction_kind,
                ),
            )
        else:
            model.reaction_kind = reaction_kind
        await self.session.flush()

    async def get_stats(self, *, date_from: date, date_to: date) -> NoteAnalyticsStats:
        daily = await self._get_daily_stats(date_from=date_from, date_to=date_to)
        note_ids = list(dict.fromkeys(item.note_id for item in daily))
        reaction_counts = await self._get_reaction_counts(note_ids=note_ids)
        notes = self._build_note_stats(daily=daily, reaction_counts=reaction_counts)
        return NoteAnalyticsStats(
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

    async def _get_daily_stats(
        self,
        *,
        date_from: date,
        date_to: date,
    ) -> list[NoteAnalyticsDailyStats]:
        result = await self.session.execute(
            select(
                NoteDailyAnalyticsModel.note_id,
                NoteModel.title,
                NoteModel.slug,
                NoteDailyAnalyticsModel.date,
                NoteDailyAnalyticsModel.source_category,
                NoteDailyAnalyticsModel.view_count,
                NoteDailyAnalyticsModel.engaged_view_count,
            )
            .join(NoteModel, NoteModel.id == NoteDailyAnalyticsModel.note_id)
            .where(
                NoteDailyAnalyticsModel.date >= date_from,
                NoteDailyAnalyticsModel.date <= date_to,
            )
            .order_by(
                NoteDailyAnalyticsModel.date,
                NoteModel.title,
                NoteDailyAnalyticsModel.source_category,
            ),
        )
        return [
            NoteAnalyticsDailyStats(
                note_id=row[0],
                title=row[1],
                slug=row[2],
                date=row[3],
                source_category=self._to_source_category(row[4]),
                view_count=row[5],
                engaged_view_count=row[6],
            )
            for row in result
        ]

    def _build_note_stats(
        self,
        *,
        daily: list[NoteAnalyticsDailyStats],
        reaction_counts: dict[UUID, NoteReactionCounts],
    ) -> list[NoteAnalyticsNoteStats]:
        note_stats: dict[UUID, NoteAnalyticsNoteStats] = {}
        for item in daily:
            existing = note_stats.get(item.note_id)
            if existing is None:
                note_stats[item.note_id] = NoteAnalyticsNoteStats(
                    note_id=item.note_id,
                    title=item.title,
                    slug=item.slug,
                    view_count=item.view_count,
                    engaged_view_count=item.engaged_view_count,
                    reaction_counts=reaction_counts.get(item.note_id, NoteReactionCounts.zero()),
                )
            else:
                note_stats[item.note_id] = NoteAnalyticsNoteStats(
                    note_id=existing.note_id,
                    title=existing.title,
                    slug=existing.slug,
                    view_count=existing.view_count + item.view_count,
                    engaged_view_count=existing.engaged_view_count + item.engaged_view_count,
                    reaction_counts=existing.reaction_counts,
                )
        return sorted(note_stats.values(), key=lambda item: (-item.view_count, item.title))

    def _build_reaction_counts(
        self,
        *,
        counts: dict[NoteReactionKind, int],
    ) -> NoteReactionCounts:
        return NoteReactionCounts(
            heart=counts.get(NoteReactionKind.HEART, 0),
            fire=counts.get(NoteReactionKind.FIRE, 0),
            thinking=counts.get(NoteReactionKind.THINKING, 0),
            neutral=counts.get(NoteReactionKind.NEUTRAL, 0),
            poop=counts.get(NoteReactionKind.POOP, 0),
        )

    def _to_reaction_kind(self, value: NoteReactionKind | str) -> NoteReactionKind:
        if isinstance(value, NoteReactionKind):
            return value
        try:
            return NoteReactionKind.from_value(value)
        except ValueError:
            return NoteReactionKind[value]

    def _to_source_category(self, value: NoteViewSourceCategory | str) -> NoteViewSourceCategory:
        if isinstance(value, NoteViewSourceCategory):
            return value
        try:
            return NoteViewSourceCategory.from_value(value)
        except ValueError:
            return NoteViewSourceCategory[value]
