from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.datastructures import State
from litestar.params import Body, Parameter

from core.auth.exceptions import ForbiddenError
from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.competency_matrix.generators import ItemIdGenerator, ResourceIdGenerator
from core.competency_matrix.use_cases import AbstractCompetencyMatrixUseCase
from core.enums import PublishStatusEnum
from core.types import IntId, SearchName
from entrypoints.litestar.api.competency_matrix.schemas import (
    CompetencyMatrixItemDetailResponseSchema,
    CompetencyMatrixItemRequestSchema,
    CompetencyMatrixItemsListResponseSchema,
    CompetencyMatrixResourcesResponseSchema,
    CompetencyMatrixSheetsListResponseSchema,
)
from entrypoints.litestar.guards import admin_user_guard


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
    )
    async def list_competency_matrix_sheet(
        self,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> CompetencyMatrixSheetsListResponseSchema:
        sheets = await use_case.list_sheets()
        return CompetencyMatrixSheetsListResponseSchema.from_domain_schema(schema=sheets)

    @get(
        "/resources/search",
        description="Поиск вопросов по матрице компетенций по названию и url.",
        name="competency-matrix-resources-search-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def search_competency_matrix_resources(
        self,
        search_name: Annotated[str, Parameter(query="searchName")],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        limit: Annotated[int, Parameter(query="limit", ge=1, le=50)],
    ) -> CompetencyMatrixResourcesResponseSchema:
        items = await use_case.find_resources(search_name=SearchName(search_name), limit=limit)
        return CompetencyMatrixResourcesResponseSchema.from_domain_schema(schema=items)

    @get(
        "/items",
        description="Получение списка вопросов по матрице компетенций.",
        name="competency-matrix-items-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_competency_matrix_items(
        self,
        request: Request[JwtUser, Token | None, State],
        sheet_name: Annotated[str, Parameter(query="sheetName")],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        only_published: Annotated[bool, Parameter(query="onlyPublished")],
    ) -> CompetencyMatrixItemsListResponseSchema:
        if not request.user.is_admin and not only_published:
            raise ForbiddenError
        items = await use_case.list_items(
            sheet_name=sheet_name,
            only_published=only_published,
        )
        return CompetencyMatrixItemsListResponseSchema.from_domain_schema(
            sheet=sheet_name,
            schema=items,
        )

    @post(
        "/items",
        description="Создание вопроса в матрице компетенций.",
        guards=[admin_user_guard],
        name="competency-matrix-item-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_competency_matrix_item(
        self,
        item_id_generator: FromDishka[ItemIdGenerator],
        resource_id_generator: FromDishka[ResourceIdGenerator],
        data: Annotated[CompetencyMatrixItemRequestSchema, Body()],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.upsert_item(
            params=data.to_schema(
                item_id_generator=item_id_generator,
                resource_id_generator=resource_id_generator,
            ),
        )
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(schema=item)

    @get(
        "/items/detail/{pk:int}",
        description="Получение подробной информации о вопросе из матрицы компетенций.",
        name="competency-matrix-item-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_competency_matrix_item(
        self,
        pk: int,
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        only_published: Annotated[bool, Parameter(query="onlyPublished")],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        if not request.user.is_admin and not only_published:
            raise ForbiddenError
        item = await use_case.get_item(item_id=IntId(pk), only_published=only_published)
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(schema=item)

    @put(
        "/items/detail/{pk:int}",
        description="Обновление вопроса в матрице компетенций.",
        guards=[admin_user_guard],
        name="competency-matrix-item-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_competency_matrix_item(
        self,
        pk: int,
        resource_id_generator: FromDishka[ResourceIdGenerator],
        data: Annotated[CompetencyMatrixItemRequestSchema, Body()],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.upsert_item(
            params=data.to_schema(
                item_id_generator=IntId(pk),
                resource_id_generator=resource_id_generator,
            ),
        )
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(schema=item)

    @delete(
        "/items/detail/{pk:int}",
        description="Удаление вопроса в матрице компетенций.",
        guards=[admin_user_guard],
        name="competency-matrix-item-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_competency_matrix_item(
        self,
        pk: int,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> None:
        await use_case.delete_item(item_id=IntId(pk))

    @post(
        "/items/detail/{pk:int}/set-draft",
        description='Установка статуса "Черновик" на вопрос в матрице компетенций.',
        guards=[admin_user_guard],
        name="competency-matrix-item-set-draft-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_draft_status_to_competency_matrix_item(
        self,
        pk: int,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> None:
        await use_case.switch_item_publish_status(
            item_id=IntId(pk),
            publish_status=PublishStatusEnum.DRAFT,
        )

    @post(
        "/items/detail/{pk:int}/set-published",
        description='Установка статуса "Опубликовано" на вопрос в матрице компетенций.',
        guards=[admin_user_guard],
        name="competency-matrix-item-set-published-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_published_status_to_competency_matrix_item(
        self,
        pk: int,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> None:
        await use_case.switch_item_publish_status(
            item_id=IntId(pk),
            publish_status=PublishStatusEnum.PUBLISHED,
        )


api_router = DishkaRouter("", route_handlers=[CompetencyMatrixApiController])
