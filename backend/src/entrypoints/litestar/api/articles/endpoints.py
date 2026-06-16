import uuid
from datetime import date
from typing import Annotated

from dishka.integrations.litestar import DishkaRouter, FromDishka
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.datastructures import State
from litestar.di import Provide
from litestar.params import Body, FromPath, QueryParameter

from core.articles.enums import ArticleViewSourceCategory
from core.articles.schemas import ArticleFilters
from core.articles.use_cases import AbstractArticleAnalyticsUseCase, AbstractArticlesUseCase
from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import IntId
from entrypoints.litestar.api.articles.dependencies import (
    provide_article_filters,
    provide_public_article_filters,
)
from entrypoints.litestar.api.articles.schemas import (
    ArticleAnalyticsStatsResponseSchema,
    ArticleDetailResponseSchema,
    ArticleListResponseSchema,
    ArticlePublicStatsCollectionResponseSchema,
    ArticleReactionRequestSchema,
    ArticleRequestSchema,
    ArticleTreeResponseSchema,
    TagRequestSchema,
    TagResponseSchema,
    TagsResponseSchema,
)
from entrypoints.litestar.guards import content_manager_guard
from entrypoints.litestar.response_cache import (
    ResponseCacheDomain,
    invalidate_and_enqueue_response_cache_warm_domain,
)
from infra.config.constants import constants
from infra.config.settings import settings


class PublicArticlesApiController(Controller):
    path = "/articles"
    tags = ["public articles"]

    @get(
        "",
        description="Получение публичного списка статей.",
        name="public-articles-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.ARTICLES.cache_key_builder,
        dependencies={"filters": Provide(provide_public_article_filters, sync_to_thread=False)},
    )
    async def list_articles(
        self,
        use_case: FromDishka[AbstractArticlesUseCase],
        filters: ArticleFilters,
    ) -> ArticleListResponseSchema:
        articles = await use_case.list_articles(filters=filters)
        return ArticleListResponseSchema.from_domain_schema(
            schema=articles,
            language=filters.language,
        )

    @get(
        "/tree",
        description="Получение публичного дерева папок и статей.",
        name="public-articles-tree-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.ARTICLES.cache_key_builder,
    )
    async def list_articles_tree(
        self,
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> ArticleTreeResponseSchema:
        tree = await use_case.list_tree(only_published=True, language=language)
        return ArticleTreeResponseSchema.from_domain_schema(schema=tree)

    @get(
        "/detail/{slug:str}",
        description="Получение публичной подробной информации о статье.",
        name="public-articles-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.ARTICLES.cache_key_builder,
    )
    async def get_article(
        self,
        slug: FromPath[str],
        use_case: FromDishka[AbstractArticlesUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> ArticleDetailResponseSchema:
        article = await use_case.get_article(slug=slug, only_published=True)
        return ArticleDetailResponseSchema.from_domain_schema(
            schema=article,
            language=language,
        )

    @get(
        "/public-stats",
        description="Получение публичной статистики статей.",
        name="public-articles-public-stats-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_public_stats(
        self,
        article_ids: Annotated[list[uuid.UUID], QueryParameter(name="articleIds", min_items=1)],
        analytics_use_case: FromDishka[AbstractArticleAnalyticsUseCase],
    ) -> ArticlePublicStatsCollectionResponseSchema:
        stats = await analytics_use_case.get_public_stats(article_ids=article_ids)
        return ArticlePublicStatsCollectionResponseSchema.from_domain_schema(schema=stats)

    @post(
        "/detail/{slug:str}/analytics/view",
        description="Фиксация публичного просмотра статьи.",
        name="public-articles-track-public-view-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def track_public_view(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractArticlesUseCase],
        analytics_use_case: FromDishka[AbstractArticleAnalyticsUseCase],
        _language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> None:
        if request.user.can_manage_content:
            return
        article = await use_case.get_article(slug=slug, only_published=True)
        await analytics_use_case.track_public_view(
            article=article,
            referrer=request.headers.get("referer"),
        )

    @post(
        "/detail/{slug:str}/analytics/engaged-view",
        description="Фиксация вовлечённого просмотра статьи.",
        name="public-articles-track-engaged-view-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def track_engaged_view(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        analytics_use_case: FromDishka[AbstractArticleAnalyticsUseCase],
        _language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> None:
        if request.user.can_manage_content:
            return
        await analytics_use_case.track_engaged_view(
            slug=slug,
            source_category=ArticleViewSourceCategory.UNKNOWN,
        )

    @post(
        "/detail/{slug:str}/reaction",
        description="Установка или снятие анонимной реакции на статью.",
        name="public-articles-set-reaction-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_reaction(
        self,
        slug: FromPath[str],
        data: Annotated[ArticleReactionRequestSchema, Body()],
        analytics_use_case: FromDishka[AbstractArticleAnalyticsUseCase],
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
        name="public-articles-tags-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.ARTICLES.cache_key_builder,
    )
    async def list_tags(
        self,
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> TagsResponseSchema:
        tags = await use_case.list_tags(include_deleted=False, language=language)
        return TagsResponseSchema.from_domain_schema(schema=tags, language=language)


class AdminArticlesApiController(Controller):
    path = "/articles"
    tags = ["admin articles"]
    guards = [content_manager_guard]

    @get(
        "",
        description="Получение админского списка статей.",
        name="admin-articles-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        dependencies={"filters": Provide(provide_article_filters, sync_to_thread=False)},
    )
    async def list_articles(
        self,
        use_case: FromDishka[AbstractArticlesUseCase],
        filters: ArticleFilters,
    ) -> ArticleListResponseSchema:
        articles = await use_case.list_articles(filters=filters)
        return ArticleListResponseSchema.from_domain_schema(
            schema=articles,
            language=filters.language,
        )

    @post(
        "",
        description="Создание статьи.",
        name="admin-articles-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_article(
        self,
        article_id: FromDishka[uuid.UUID],
        request: Request[JwtUser, Token | None, State],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        data: Annotated[ArticleRequestSchema, Body()],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> ArticleDetailResponseSchema:
        article = await use_case.create_article(
            params=data.to_create_schema(
                article_id=article_id,
                author_username=request.user.username,
            ),
        )
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.ARTICLES,
        )
        return ArticleDetailResponseSchema.from_domain_schema(
            schema=article,
            language=language,
        )

    @get(
        "/tree",
        description="Получение админского дерева папок и статей.",
        name="admin-articles-tree-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_articles_tree(
        self,
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> ArticleTreeResponseSchema:
        tree = await use_case.list_tree(only_published=False, language=language)
        return ArticleTreeResponseSchema.from_domain_schema(schema=tree)

    @get(
        "/detail/{slug:str}",
        description="Получение админской подробной информации о статье.",
        name="admin-articles-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_article(
        self,
        slug: FromPath[str],
        use_case: FromDishka[AbstractArticlesUseCase],
        only_published: Annotated[bool, QueryParameter(name="onlyPublished")],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> ArticleDetailResponseSchema:
        article = await use_case.get_article(slug=slug, only_published=only_published)
        return ArticleDetailResponseSchema.from_domain_schema(
            schema=article,
            language=language,
        )

    @get(
        "/stats",
        description="Получение админской статистики статей.",
        name="admin-articles-stats-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_stats(
        self,
        analytics_use_case: FromDishka[AbstractArticleAnalyticsUseCase],
        date_from: Annotated[date, QueryParameter(name="dateFrom")],
        date_to: Annotated[date, QueryParameter(name="dateTo")],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> ArticleAnalyticsStatsResponseSchema:
        stats = await analytics_use_case.get_stats(
            date_from=date_from,
            date_to=date_to,
            language=language,
        )
        return ArticleAnalyticsStatsResponseSchema.from_domain_schema(schema=stats)

    @put(
        "/detail/{slug:str}",
        description="Обновление статьи.",
        name="admin-articles-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_article(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        data: Annotated[ArticleRequestSchema, Body()],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> ArticleDetailResponseSchema:
        article = await use_case.update_article(
            slug=slug,
            params=data.to_update_schema(),
        )
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.ARTICLES,
        )
        return ArticleDetailResponseSchema.from_domain_schema(
            schema=article,
            language=language,
        )

    @delete(
        "/detail/{slug:str}",
        description="Удаление статьи.",
        name="admin-articles-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_article(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> None:
        await use_case.delete_article(slug=slug)
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.ARTICLES,
        )

    @post(
        "/detail/{slug:str}/set-draft",
        description='Установка статуса "Черновик" на статью.',
        name="admin-articles-set-draft-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_draft_status_to_article(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> None:
        await use_case.switch_article_publish_status(
            slug=slug,
            publish_status=PublishStatusEnum.DRAFT,
        )
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.ARTICLES,
        )

    @post(
        "/detail/{slug:str}/set-published",
        description='Установка статуса "Опубликовано" на статью.',
        name="admin-articles-set-published-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_published_status_to_article(
        self,
        slug: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> None:
        await use_case.switch_article_publish_status(
            slug=slug,
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.ARTICLES,
        )

    @get(
        "/tags",
        description="Получение админского списка тегов.",
        name="admin-articles-tags-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_tags(
        self,
        include_deleted: Annotated[bool, QueryParameter(name="includeDeleted")],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> TagsResponseSchema:
        tags = await use_case.list_tags(include_deleted=include_deleted, language=language)
        return TagsResponseSchema.from_domain_schema(schema=tags, language=language)

    @get(
        "/tags/search",
        description="Админский поиск тегов.",
        name="admin-articles-tags-search-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def search_tags(
        self,
        search_name: Annotated[str, QueryParameter(name="searchName")],
        include_deleted: Annotated[bool, QueryParameter(name="includeDeleted")],
        limit: Annotated[int, QueryParameter(name="limit", ge=1, le=50)],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        use_case: FromDishka[AbstractArticlesUseCase],
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
        name="admin-articles-tags-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_tag(
        self,
        tag_id: FromDishka[IntId],
        request: Request[JwtUser, Token | None, State],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        data: Annotated[TagRequestSchema, Body()],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> TagResponseSchema:
        tag = await use_case.create_tag(
            params=data.to_create_schema(tag_id=tag_id),
        )
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.ARTICLES,
        )
        return TagResponseSchema.from_domain_schema(schema=tag, language=language)

    @put(
        "/tags/{tag_id:int}",
        description="Обновление тега.",
        name="admin-articles-tags-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_tag(
        self,
        tag_id: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
        data: Annotated[TagRequestSchema, Body()],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> TagResponseSchema:
        tag = await use_case.update_tag(
            tag_id=IntId(tag_id),
            params=data.to_update_schema(),
        )
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.ARTICLES,
        )
        return TagResponseSchema.from_domain_schema(schema=tag, language=language)

    @delete(
        "/tags/{tag_id:int}",
        description="Удаление тега.",
        name="admin-articles-tags-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_tag(
        self,
        tag_id: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> None:
        await use_case.soft_delete_tag(tag_id=IntId(tag_id))
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.ARTICLES,
        )

    @post(
        "/tags/{tag_id:int}/restore",
        description="Восстановление тега.",
        name="admin-articles-tags-restore-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def restore_tag(
        self,
        tag_id: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractArticlesUseCase],
    ) -> None:
        await use_case.restore_tag(tag_id=IntId(tag_id))
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.ARTICLES,
        )


api_router = DishkaRouter("", route_handlers=[PublicArticlesApiController])
admin_router = DishkaRouter("", route_handlers=[AdminArticlesApiController])
