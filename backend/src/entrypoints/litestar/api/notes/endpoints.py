import uuid
from datetime import date
from typing import Annotated

from dishka.integrations.litestar import DishkaRouter, FromDishka
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.datastructures import State
from litestar.di import Provide
from litestar.params import Body, FromPath, QueryParameter

from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.notes.enums import NoteViewSourceCategory
from core.notes.schemas import NoteFilters
from core.notes.use_cases import AbstractNoteAnalyticsUseCase, AbstractNotesUseCase
from core.types import IntId
from entrypoints.litestar.api.notes.dependencies import (
    provide_note_filters,
    provide_public_note_filters,
)
from entrypoints.litestar.api.notes.schemas import (
    NoteAnalyticsStatsResponseSchema,
    NoteDetailResponseSchema,
    NoteListResponseSchema,
    NotePublicStatsCollectionResponseSchema,
    NoteReactionRequestSchema,
    NoteRequestSchema,
    NoteTreeResponseSchema,
    TagRequestSchema,
    TagResponseSchema,
    TagsResponseSchema,
)
from entrypoints.litestar.guards import content_manager_guard
from entrypoints.litestar.response_cache import (
    ResponseCacheDomain,
    invalidate_response_cache_domain,
)
from infra.config.constants import constants
from infra.config.settings import settings


class PublicNotesApiController(Controller):
    path = "/notes"
    tags = ["public notes"]

    @get(
        "",
        description="Получение публичного списка заметок.",
        name="public-notes-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.NOTES.cache_key_builder,
        dependencies={"filters": Provide(provide_public_note_filters, sync_to_thread=False)},
    )
    async def list_notes(
        self,
        use_case: FromDishka[AbstractNotesUseCase],
        filters: NoteFilters,
    ) -> NoteListResponseSchema:
        notes = await use_case.list_notes(filters=filters)
        return NoteListResponseSchema.from_domain_schema(
            schema=notes,
            language=filters.language,
        )

    @get(
        "/tree",
        description="Получение публичного дерева папок и заметок.",
        name="public-notes-tree-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.NOTES.cache_key_builder,
    )
    async def list_notes_tree(
        self,
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> NoteTreeResponseSchema:
        tree = await use_case.list_tree(only_published=True, language=language)
        return NoteTreeResponseSchema.from_domain_schema(schema=tree)

    @get(
        "/detail/{slug:str}",
        description="Получение публичной подробной информации о заметке.",
        name="public-notes-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.NOTES.cache_key_builder,
    )
    async def get_note(
        self,
        slug: FromPath[str],
        use_case: FromDishka[AbstractNotesUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> NoteDetailResponseSchema:
        note = await use_case.get_note(slug=slug, only_published=True)
        return NoteDetailResponseSchema.from_domain_schema(
            schema=note,
            language=language,
        )

    @get(
        "/public-stats",
        description="Получение публичной статистики заметок.",
        name="public-notes-public-stats-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_public_stats(
        self,
        note_ids: Annotated[list[uuid.UUID], QueryParameter(name="noteIds", min_items=1)],
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
    ) -> NotePublicStatsCollectionResponseSchema:
        stats = await analytics_use_case.get_public_stats(note_ids=note_ids)
        return NotePublicStatsCollectionResponseSchema.from_domain_schema(schema=stats)

    @post(
        "/detail/{slug:str}/analytics/view",
        description="Фиксация публичного просмотра заметки.",
        name="public-notes-track-public-view-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def track_public_view(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractNotesUseCase],
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
        _language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> None:
        if request.user.can_manage_content:
            return
        note = await use_case.get_note(slug=slug, only_published=True)
        await analytics_use_case.track_public_view(
            note=note,
            referrer=request.headers.get("referer"),
        )

    @post(
        "/detail/{slug:str}/analytics/engaged-view",
        description="Фиксация вовлечённого просмотра заметки.",
        name="public-notes-track-engaged-view-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def track_engaged_view(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
        _language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> None:
        if request.user.can_manage_content:
            return
        await analytics_use_case.track_engaged_view(
            slug=slug,
            source_category=NoteViewSourceCategory.UNKNOWN,
        )

    @post(
        "/detail/{slug:str}/reaction",
        description="Установка или снятие анонимной реакции на заметку.",
        name="public-notes-set-reaction-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_reaction(
        self,
        slug: FromPath[str],
        data: Annotated[NoteReactionRequestSchema, Body()],
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
        _language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> None:
        await analytics_use_case.set_reaction(
            slug=slug,
            client_token=data.client_token,
            reaction_kind=data.reaction_kind,
        )

    @get(
        "/tags",
        description="Получение публичного списка тегов.",
        name="public-notes-tags-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.NOTES.cache_key_builder,
    )
    async def list_tags(
        self,
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> TagsResponseSchema:
        tags = await use_case.list_tags(include_deleted=False, language=language)
        return TagsResponseSchema.from_domain_schema(schema=tags, language=language)


class AdminNotesApiController(Controller):
    path = "/notes"
    tags = ["admin notes"]
    guards = [content_manager_guard]

    @get(
        "",
        description="Получение админского списка заметок.",
        name="admin-notes-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        dependencies={"filters": Provide(provide_note_filters, sync_to_thread=False)},
    )
    async def list_notes(
        self,
        use_case: FromDishka[AbstractNotesUseCase],
        filters: NoteFilters,
    ) -> NoteListResponseSchema:
        notes = await use_case.list_notes(filters=filters)
        return NoteListResponseSchema.from_domain_schema(
            schema=notes,
            language=filters.language,
        )

    @post(
        "",
        description="Создание заметки.",
        name="admin-notes-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_note(
        self,
        note_id: FromDishka[uuid.UUID],
        request: Request[JwtUser, Token | None, State],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        data: Annotated[NoteRequestSchema, Body()],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> NoteDetailResponseSchema:
        note = await use_case.create_note(
            params=data.to_create_schema(
                note_id=note_id,
                author_username=request.user.username,
            ),
        )
        await invalidate_response_cache_domain(request=request, domain=ResponseCacheDomain.NOTES)
        return NoteDetailResponseSchema.from_domain_schema(
            schema=note,
            language=language,
        )

    @get(
        "/tree",
        description="Получение админского дерева папок и заметок.",
        name="admin-notes-tree-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_notes_tree(
        self,
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> NoteTreeResponseSchema:
        tree = await use_case.list_tree(only_published=False, language=language)
        return NoteTreeResponseSchema.from_domain_schema(schema=tree)

    @get(
        "/detail/{slug:str}",
        description="Получение админской подробной информации о заметке.",
        name="admin-notes-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_note(
        self,
        slug: FromPath[str],
        use_case: FromDishka[AbstractNotesUseCase],
        only_published: Annotated[bool, QueryParameter(name="onlyPublished")],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> NoteDetailResponseSchema:
        note = await use_case.get_note(slug=slug, only_published=only_published)
        return NoteDetailResponseSchema.from_domain_schema(
            schema=note,
            language=language,
        )

    @get(
        "/stats",
        description="Получение админской статистики заметок.",
        name="admin-notes-stats-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_stats(
        self,
        analytics_use_case: FromDishka[AbstractNoteAnalyticsUseCase],
        date_from: Annotated[date, QueryParameter(name="dateFrom")],
        date_to: Annotated[date, QueryParameter(name="dateTo")],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> NoteAnalyticsStatsResponseSchema:
        stats = await analytics_use_case.get_stats(
            date_from=date_from,
            date_to=date_to,
            language=language,
        )
        return NoteAnalyticsStatsResponseSchema.from_domain_schema(schema=stats)

    @put(
        "/detail/{slug:str}",
        description="Обновление заметки.",
        name="admin-notes-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_note(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        data: Annotated[NoteRequestSchema, Body()],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> NoteDetailResponseSchema:
        note = await use_case.update_note(
            slug=slug,
            params=data.to_update_schema(),
        )
        await invalidate_response_cache_domain(request=request, domain=ResponseCacheDomain.NOTES)
        return NoteDetailResponseSchema.from_domain_schema(
            schema=note,
            language=language,
        )

    @delete(
        "/detail/{slug:str}",
        description="Удаление заметки.",
        name="admin-notes-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_note(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> None:
        await use_case.delete_note(slug=slug)
        await invalidate_response_cache_domain(request=request, domain=ResponseCacheDomain.NOTES)

    @post(
        "/detail/{slug:str}/set-draft",
        description='Установка статуса "Черновик" на заметку.',
        name="admin-notes-set-draft-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_draft_status_to_note(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> None:
        await use_case.switch_note_publish_status(
            slug=slug,
            publish_status=PublishStatusEnum.DRAFT,
        )
        await invalidate_response_cache_domain(request=request, domain=ResponseCacheDomain.NOTES)

    @post(
        "/detail/{slug:str}/set-published",
        description='Установка статуса "Опубликовано" на заметку.',
        name="admin-notes-set-published-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_published_status_to_note(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> None:
        await use_case.switch_note_publish_status(
            slug=slug,
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        await invalidate_response_cache_domain(request=request, domain=ResponseCacheDomain.NOTES)

    @get(
        "/tags",
        description="Получение админского списка тегов.",
        name="admin-notes-tags-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_tags(
        self,
        include_deleted: Annotated[bool, QueryParameter(name="includeDeleted")],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> TagsResponseSchema:
        tags = await use_case.list_tags(include_deleted=include_deleted, language=language)
        return TagsResponseSchema.from_domain_schema(schema=tags, language=language)

    @get(
        "/tags/search",
        description="Админский поиск тегов.",
        name="admin-notes-tags-search-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def search_tags(
        self,
        search_name: Annotated[str, QueryParameter(name="searchName")],
        include_deleted: Annotated[bool, QueryParameter(name="includeDeleted")],
        limit: Annotated[int, QueryParameter(name="limit", ge=1, le=50)],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> TagsResponseSchema:
        tags = await use_case.search_tags(
            search_name=search_name,
            include_deleted=include_deleted,
            limit=limit,
            language=language,
        )
        return TagsResponseSchema.from_domain_schema(schema=tags, language=language)

    @post(
        "/tags",
        description="Создание тега.",
        name="admin-notes-tags-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_tag(
        self,
        tag_id: FromDishka[IntId],
        request: Request[JwtUser, Token | None, State],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        data: Annotated[TagRequestSchema, Body()],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> TagResponseSchema:
        tag = await use_case.create_tag(
            params=data.to_create_schema(tag_id=tag_id),
        )
        await invalidate_response_cache_domain(request=request, domain=ResponseCacheDomain.NOTES)
        return TagResponseSchema.from_domain_schema(schema=tag, language=language)

    @put(
        "/tags/{tag_id:int}",
        description="Обновление тега.",
        name="admin-notes-tags-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_tag(
        self,
        tag_id: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        data: Annotated[TagRequestSchema, Body()],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> TagResponseSchema:
        tag = await use_case.update_tag(
            tag_id=IntId(tag_id),
            params=data.to_update_schema(),
        )
        await invalidate_response_cache_domain(request=request, domain=ResponseCacheDomain.NOTES)
        return TagResponseSchema.from_domain_schema(schema=tag, language=language)

    @delete(
        "/tags/{tag_id:int}",
        description="Удаление тега.",
        name="admin-notes-tags-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_tag(
        self,
        tag_id: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> None:
        await use_case.soft_delete_tag(tag_id=IntId(tag_id))
        await invalidate_response_cache_domain(request=request, domain=ResponseCacheDomain.NOTES)

    @post(
        "/tags/{tag_id:int}/restore",
        description="Восстановление тега.",
        name="admin-notes-tags-restore-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def restore_tag(
        self,
        tag_id: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractNotesUseCase],
    ) -> None:
        await use_case.restore_tag(tag_id=IntId(tag_id))
        await invalidate_response_cache_domain(request=request, domain=ResponseCacheDomain.NOTES)


api_router = DishkaRouter("", route_handlers=[PublicNotesApiController])
admin_router = DishkaRouter("", route_handlers=[AdminNotesApiController])
