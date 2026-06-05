from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.config.response_cache import CACHE_FOREVER
from litestar.datastructures import State
from litestar.params import Body, FromPath, QueryParameter

from core.auth.exceptions import ForbiddenError
from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.competency_matrix.generators import ItemIdGenerator, ResourceIdGenerator
from core.competency_matrix.schemas import CompetencyMatrixItemFilters
from core.competency_matrix.use_cases import AbstractCompetencyMatrixUseCase
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import IntId, SearchName
from entrypoints.litestar.api.competency_matrix.schemas import (
    CompetencyMatrixItemDetailResponseSchema,
    CompetencyMatrixItemRequestSchema,
    CompetencyMatrixItemsListResponseSchema,
    CompetencyMatrixResourcesResponseSchema,
    CompetencyMatrixSheetsListResponseSchema,
)
from entrypoints.litestar.guards import content_manager_guard, draft_content_access_guard
from entrypoints.litestar.response_cache import (
    ResponseCacheDomain,
    invalidate_response_cache_domain,
)
from infra.config.settings import settings


class CompetencyMatrixApiController(Controller):
    path = "/competency-matrix"
    tags = ["competency matrix"]

    @get(
        "/sheets",
        description=(
            "Получение списка листов матрицы компетенций. Список содержит только доступные листы "
            "без вывода вопросов по ним. Сделайте запрос на ручку `items/` с параметром sheetId, "
            "чтобы получить вопросы по нужному листу."
        ),
        name="competency-matrix-sheets-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(CACHE_FOREVER),
        cache_key_builder=ResponseCacheDomain.COMPETENCY_MATRIX.cache_key_builder,
    )
    async def list_competency_matrix_sheet(
        self,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixSheetsListResponseSchema:
        sheets = await use_case.list_sheets()
        return CompetencyMatrixSheetsListResponseSchema.from_domain_schema(
            schema=sheets,
            language=language,
        )

    @get(
        "/resources/search",
        description="Поиск вопросов по матрице компетенций по названию и url.",
        name="competency-matrix-resources-search-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(CACHE_FOREVER),
        cache_key_builder=ResponseCacheDomain.COMPETENCY_MATRIX.cache_key_builder,
    )
    async def search_competency_matrix_resources(
        self,
        search_name: Annotated[str, QueryParameter(name="searchName")],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        limit: Annotated[int, QueryParameter(name="limit", ge=1, le=50)],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixResourcesResponseSchema:
        items = await use_case.find_resources(
            search_name=SearchName(search_name),
            limit=limit,
            language=language,
        )
        return CompetencyMatrixResourcesResponseSchema.from_domain_schema(
            schema=items,
            language=language,
        )

    @get(
        "/items",
        description="Получение списка вопросов по матрице компетенций.",
        guards=[draft_content_access_guard],
        name="competency-matrix-items-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(CACHE_FOREVER),
        cache_key_builder=ResponseCacheDomain.COMPETENCY_MATRIX.cache_key_builder,
    )
    async def list_competency_matrix_items(
        self,
        request: Request[JwtUser, Token | None, State],
        sheet_key: Annotated[str, QueryParameter(name="sheetKey")],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        only_published: Annotated[bool, QueryParameter(name="onlyPublished")],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemsListResponseSchema:
        if not request.user.can_manage_content and not only_published:
            raise ForbiddenError
        filters = CompetencyMatrixItemFilters(
            sheet_key=sheet_key,
            only_published=only_published,
        )
        items = await use_case.list_items(filters=filters)
        return CompetencyMatrixItemsListResponseSchema.from_domain_schema(
            sheet_key=sheet_key,
            schema=items,
            language=language,
        )

    @post(
        "/items",
        description="Создание вопроса в матрице компетенций.",
        guards=[content_manager_guard],
        name="competency-matrix-item-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_competency_matrix_item(  # noqa: PLR0913
        self,
        item_id_generator: FromDishka[ItemIdGenerator],
        resource_id_generator: FromDishka[ResourceIdGenerator],
        request: Request[JwtUser, Token | None, State],
        data: Annotated[CompetencyMatrixItemRequestSchema, Body()],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.create_item(
            params=data.to_create_schema(
                item_id_generator=item_id_generator,
                resource_id_generator=resource_id_generator,
            ),
        )
        await invalidate_response_cache_domain(
            request=request,
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
        )
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
            schema=item,
            language=language,
        )

    @get(
        "/items/detail/{pk:int}",
        description="Получение подробной информации о вопросе из матрицы компетенций.",
        guards=[draft_content_access_guard],
        name="competency-matrix-item-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(CACHE_FOREVER),
        cache_key_builder=ResponseCacheDomain.COMPETENCY_MATRIX.cache_key_builder,
    )
    async def get_competency_matrix_item(
        self,
        pk: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        only_published: Annotated[bool, QueryParameter(name="onlyPublished")],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        if not request.user.can_manage_content and not only_published:
            raise ForbiddenError
        item = await use_case.get_item(item_id=IntId(pk), only_published=only_published)
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
            schema=item,
            language=language,
        )

    @get(
        "/items/public/{slug:str}",
        description="Получение публичной подробной информации о вопросе матрицы по slug.",
        name="competency-matrix-public-item-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(CACHE_FOREVER),
        cache_key_builder=ResponseCacheDomain.COMPETENCY_MATRIX.cache_key_builder,
    )
    async def get_public_competency_matrix_item(
        self,
        slug: FromPath[str],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.get_item_by_slug(slug=slug, only_published=True)
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
            schema=item,
            language=language,
        )

    @put(
        "/items/detail/{pk:int}",
        description="Обновление вопроса в матрице компетенций.",
        guards=[content_manager_guard],
        name="competency-matrix-item-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_competency_matrix_item(  # noqa: PLR0913
        self,
        pk: FromPath[int],
        resource_id_generator: FromDishka[ResourceIdGenerator],
        request: Request[JwtUser, Token | None, State],
        data: Annotated[CompetencyMatrixItemRequestSchema, Body()],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.update_item(
            params=data.to_update_schema(
                item_id=IntId(pk),
                resource_id_generator=resource_id_generator,
            ),
        )
        await invalidate_response_cache_domain(
            request=request,
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
        )
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
            schema=item,
            language=language,
        )

    @delete(
        "/items/detail/{pk:int}",
        description="Удаление вопроса в матрице компетенций.",
        guards=[content_manager_guard],
        name="competency-matrix-item-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_competency_matrix_item(
        self,
        pk: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> None:
        await use_case.delete_item(item_id=IntId(pk))
        await invalidate_response_cache_domain(
            request=request,
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
        )

    @post(
        "/items/detail/{pk:int}/set-draft",
        description='Установка статуса "Черновик" на вопрос в матрице компетенций.',
        guards=[content_manager_guard],
        name="competency-matrix-item-set-draft-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_draft_status_to_competency_matrix_item(
        self,
        pk: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> None:
        await use_case.switch_item_publish_status(
            item_id=IntId(pk),
            publish_status=PublishStatusEnum.DRAFT,
        )
        await invalidate_response_cache_domain(
            request=request,
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
        )

    @post(
        "/items/detail/{pk:int}/set-published",
        description='Установка статуса "Опубликовано" на вопрос в матрице компетенций.',
        guards=[content_manager_guard],
        name="competency-matrix-item-set-published-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_published_status_to_competency_matrix_item(
        self,
        pk: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> None:
        await use_case.switch_item_publish_status(
            item_id=IntId(pk),
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        await invalidate_response_cache_domain(
            request=request,
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
        )


api_router = DishkaRouter("", route_handlers=[CompetencyMatrixApiController])
