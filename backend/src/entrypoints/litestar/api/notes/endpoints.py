import uuid
from datetime import date
from typing import Annotated

from dishka.integrations.litestar import DishkaRouter, FromDishka
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.datastructures import State
from litestar.params import Body, Parameter

from core.auth.exceptions import ForbiddenError
from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.enums import PublishStatusEnum
from core.notes.enums import NoteViewSourceCategory
from core.notes.schemas import NoteFilters
from core.notes.use_cases import AbstractNoteAnalyticsUseCase, AbstractNotesUseCase
from core.types import IntId
from entrypoints.litestar.api.notes.schemas import (
    NoteAnalyticsStatsResponseSchema,
    NoteDetailResponseSchema,
    NoteListResponseSchema,
    NoteReactionRequestSchema,
    NoteRequestSchema,
    NoteTreeResponseSchema,
    TagRequestSchema,
    TagResponseSchema,
    TagsResponseSchema,
)
from entrypoints.litestar.guards import admin_user_guard, deleted_tags_access_guard


class NotesApiController(Controller):
    path = "/notes"
    tags = ["notes"]

    @get(
        "",
        description="Получение списка заметок.",
        name="notes-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_notes(  # noqa: PLR0913
        self,
        request: Request[JwtUser, Token | None, State],
        page: Annotated[int, Parameter(query="page", ge=1)],
        page_size: Annotated[int, Parameter(query="pageSize", ge=1, le=100)],
        only_published: Annotated[bool, Parameter(query="onlyPublished")],
        use_case: FromDishka[AbstractNotesUseCase],
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
        tag_slug: Annotated[str | None, Parameter(query="tagSlug")] = None,
    ) -> NoteListResponseSchema:
        if not request.user.is_admin and not only_published:
            raise ForbiddenError
        notes = await use_case.list_notes(
            filters=NoteFilters(
                page=page,
                page_size=page_size,
                only_published=only_published,
                tag_slug=tag_slug,
            ),
        )
        stats = await analytics_use_case.get_public_stats(
            note_ids=[note.id for note in notes.values],
        )
        return NoteListResponseSchema.from_domain_schema(schema=notes, stats=stats)

    @post(
        "",
        description="Создание заметки.",
        guards=[admin_user_guard],
        name="notes-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_note(
        self,
        note_id: FromDishka[uuid.UUID],
        request: Request[JwtUser, Token | None, State],
        data: Annotated[NoteRequestSchema, Body()],
        use_case: FromDishka[AbstractNotesUseCase],
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
    ) -> NoteDetailResponseSchema:
        note = await use_case.create_note(
            params=data.to_create_schema(
                note_id=note_id,
                author_username=request.user.username,
            ),
        )
        stats = await analytics_use_case.get_public_stats(note_ids=[note.id])
        return NoteDetailResponseSchema.from_domain_schema(
            schema=note,
            stats=stats.by_note_id(note.id),
        )

    @get(
        "/tree",
        description="Получение дерева папок и заметок.",
        name="notes-tree-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_notes_tree(
        self,
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> NoteTreeResponseSchema:
        tree = await use_case.list_tree(only_published=not request.user.is_admin)
        return NoteTreeResponseSchema.from_domain_schema(schema=tree)

    @get(
        "/detail/{slug:str}",
        description="Получение подробной информации о заметке.",
        name="notes-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_note(
        self,
        slug: str,
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractNotesUseCase],
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
        only_published: Annotated[bool, Parameter(query="onlyPublished")],
    ) -> NoteDetailResponseSchema:
        if not request.user.is_admin and not only_published:
            raise ForbiddenError
        note = await use_case.get_note(slug=slug, only_published=only_published)
        if not request.user.is_admin and only_published:
            await analytics_use_case.track_public_view(
                note=note,
                referrer=request.headers.get("referer"),
            )
        stats = await analytics_use_case.get_public_stats(note_ids=[note.id])
        return NoteDetailResponseSchema.from_domain_schema(
            schema=note,
            stats=stats.by_note_id(note.id),
        )

    @post(
        "/detail/{slug:str}/analytics/engaged-view",
        description="Фиксация вовлечённого просмотра заметки.",
        name="notes-track-engaged-view-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def track_engaged_view(
        self,
        slug: str,
        request: Request[JwtUser, Token | None, State],
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
    ) -> None:
        if request.user.is_admin:
            return
        await analytics_use_case.track_engaged_view(
            slug=slug,
            source_category=NoteViewSourceCategory.UNKNOWN,
        )

    @post(
        "/detail/{slug:str}/reaction",
        description="Установка или снятие анонимной реакции на заметку.",
        name="notes-set-reaction-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_reaction(
        self,
        slug: str,
        data: Annotated[NoteReactionRequestSchema, Body()],
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
    ) -> None:
        await analytics_use_case.set_reaction(
            slug=slug,
            client_token=data.client_token,
            reaction_kind=data.reaction_kind,
        )

    @get(
        "/stats",
        description="Получение статистики заметок.",
        guards=[admin_user_guard],
        name="notes-stats-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_stats(
        self,
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
        date_from: Annotated[date, Parameter(query="dateFrom")],
        date_to: Annotated[date, Parameter(query="dateTo")],
    ) -> NoteAnalyticsStatsResponseSchema:
        stats = await analytics_use_case.get_stats(date_from=date_from, date_to=date_to)
        return NoteAnalyticsStatsResponseSchema.from_domain_schema(schema=stats)

    @put(
        "/detail/{slug:str}",
        description="Обновление заметки.",
        guards=[admin_user_guard],
        name="notes-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_note(
        self,
        slug: str,
        data: Annotated[NoteRequestSchema, Body()],
        use_case: FromDishka[AbstractNotesUseCase],
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
    ) -> NoteDetailResponseSchema:
        note = await use_case.update_note(slug=slug, params=data.to_update_schema())
        stats = await analytics_use_case.get_public_stats(note_ids=[note.id])
        return NoteDetailResponseSchema.from_domain_schema(
            schema=note,
            stats=stats.by_note_id(note.id),
        )

    @delete(
        "/detail/{slug:str}",
        description="Удаление заметки.",
        guards=[admin_user_guard],
        name="notes-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_note(
        self,
        slug: str,
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> None:
        await use_case.delete_note(slug=slug)

    @post(
        "/detail/{slug:str}/set-draft",
        description='Установка статуса "Черновик" на заметку.',
        guards=[admin_user_guard],
        name="notes-set-draft-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_draft_status_to_note(
        self,
        slug: str,
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> None:
        await use_case.switch_note_publish_status(
            slug=slug,
            publish_status=PublishStatusEnum.DRAFT,
        )

    @post(
        "/detail/{slug:str}/set-published",
        description='Установка статуса "Опубликовано" на заметку.',
        guards=[admin_user_guard],
        name="notes-set-published-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_published_status_to_note(
        self,
        slug: str,
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> None:
        await use_case.switch_note_publish_status(
            slug=slug,
            publish_status=PublishStatusEnum.PUBLISHED,
        )

    @get(
        "/tags",
        description="Получение списка тегов.",
        guards=[deleted_tags_access_guard],
        name="notes-tags-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_tags(
        self,
        include_deleted: Annotated[bool, Parameter(query="includeDeleted")],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> TagsResponseSchema:
        tags = await use_case.list_tags(include_deleted=include_deleted)
        return TagsResponseSchema.from_domain_schema(schema=tags)

    @get(
        "/tags/search",
        description="Поиск тегов.",
        guards=[deleted_tags_access_guard],
        name="notes-tags-search-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def search_tags(
        self,
        search_name: Annotated[str, Parameter(query="searchName")],
        include_deleted: Annotated[bool, Parameter(query="includeDeleted")],
        limit: Annotated[int, Parameter(query="limit", ge=1, le=50)],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> TagsResponseSchema:
        tags = await use_case.search_tags(
            search_name=search_name,
            include_deleted=include_deleted,
            limit=limit,
        )
        return TagsResponseSchema.from_domain_schema(schema=tags)

    @post(
        "/tags",
        description="Создание тега.",
        guards=[admin_user_guard],
        name="notes-tags-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_tag(
        self,
        tag_id: FromDishka[IntId],
        data: Annotated[TagRequestSchema, Body()],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> TagResponseSchema:
        tag = await use_case.create_tag(params=data.to_create_schema(tag_id=tag_id))
        return TagResponseSchema.from_domain_schema(schema=tag)

    @put(
        "/tags/{tag_id:int}",
        description="Обновление тега.",
        guards=[admin_user_guard],
        name="notes-tags-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_tag(
        self,
        tag_id: int,
        data: Annotated[TagRequestSchema, Body()],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> TagResponseSchema:
        tag = await use_case.update_tag(tag_id=IntId(tag_id), params=data.to_update_schema())
        return TagResponseSchema.from_domain_schema(schema=tag)

    @delete(
        "/tags/{tag_id:int}",
        description="Удаление тега.",
        guards=[admin_user_guard],
        name="notes-tags-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_tag(
        self,
        tag_id: int,
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> None:
        await use_case.soft_delete_tag(tag_id=IntId(tag_id))

    @post(
        "/tags/{tag_id:int}/restore",
        description="Восстановление тега.",
        guards=[admin_user_guard],
        name="notes-tags-restore-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def restore_tag(
        self,
        tag_id: int,
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> None:
        await use_case.restore_tag(tag_id=IntId(tag_id))


api_router = DishkaRouter("", route_handlers=[NotesApiController])
