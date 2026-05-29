from dataclasses import dataclass
from datetime import UTC, datetime
from math import ceil
from typing import Any, TypeVar

from sqlalchemy import Select, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.enums import PublishStatusEnum
from core.notes.exceptions import NoteNotFoundError, TagNotFoundError
from core.notes.schemas import (
    Note,
    NoteFilters,
    NoteList,
    NoteTree,
    NoteTreeFolder,
    NoteTreeItem,
    Tag,
    Tags,
)
from core.notes.storages import NotesStorage
from core.types import IntId
from infra.postgresql.models import NoteModel, NoteToTagSecondaryModel, TagModel

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

    async def list_notes(self, *, filters: NoteFilters) -> NoteList:
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

        return NoteList(
            notes=[
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
