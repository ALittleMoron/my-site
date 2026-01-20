from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.datastructures import State
from litestar.params import Body, Parameter

from config.settings import settings
from core.auth.exceptions import ForbiddenError
from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.competency_matrix.generators import ItemIdGenerator, ResourceIdGenerator
from core.competency_matrix.use_cases import (
    AbstractDeleteItemUseCase,
    AbstractFindResourcesUseCase,
    AbstractGetItemUseCase,
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
    AbstractPublishSwitchItemUseCase,
    AbstractUpsertItemUseCase,
)
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
        cache=settings.app.get_cache_duration(120),  # 2 минуты
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_competency_matrix_sheet(
        self,
        use_case: FromDishka[AbstractListSheetsUseCase],
    ) -> CompetencyMatrixSheetsListResponseSchema:
        sheets = await use_case.execute()
        return CompetencyMatrixSheetsListResponseSchema.from_domain_schema(schema=sheets)

    @get(
        "/resources/search",
        description="Поиск вопросов по матрице компетенций по названию и url.",
        cache=settings.app.get_cache_duration(10),  # 10 секунд
        status_code=status_codes.HTTP_200_OK,
    )
    async def search_competency_matrix_resources(
        self,
        search_name: Annotated[str, Parameter(query="searchName")],
        use_case: FromDishka[AbstractFindResourcesUseCase],
    ) -> CompetencyMatrixResourcesResponseSchema:
        items = await use_case.execute(search_name=SearchName(search_name))
        return CompetencyMatrixResourcesResponseSchema.from_domain_schema(schema=items)

    @get(
        "/items",
        description="Получение списка вопросов по матрице компетенций.",
        cache=settings.app.get_cache_duration(60),  # 1 минута
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_competency_matrix_items(
        self,
        request: Request[JwtUser, Token, State],
        sheet_name: Annotated[str, Parameter(query="sheetName")],
        use_case: FromDishka[AbstractListItemsUseCase],
        only_published: Annotated[bool, Parameter(query="onlyPublished")] = True,  # noqa: FBT002
    ) -> CompetencyMatrixItemsListResponseSchema:
        if not request.user.is_admin and not only_published:
            raise ForbiddenError
        items = await use_case.execute(
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
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_competency_matrix_item(
        self,
        item_id_generator: FromDishka[ItemIdGenerator],
        resource_id_generator: FromDishka[ResourceIdGenerator],
        data: Annotated[CompetencyMatrixItemRequestSchema, Body()],
        use_case: FromDishka[AbstractUpsertItemUseCase],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.execute(
            params=data.to_schema(
                item_id_generator=item_id_generator,
                resource_id_generator=resource_id_generator,
            ),
        )
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(schema=item)

    @get(
        "/items/detail/{pk:int}",
        description="Получение подробной информации о вопросе из матрицы компетенций.",
        cache=settings.app.get_cache_duration(15),  # 15 секунд
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_competency_matrix_item(
        self,
        pk: int,
        request: Request[JwtUser, Token, State],
        use_case: FromDishka[AbstractGetItemUseCase],
        only_published: Annotated[bool, Parameter(query="onlyPublished")] = True,  # noqa: FBT002
    ) -> CompetencyMatrixItemDetailResponseSchema:
        if not request.user.is_admin and not only_published:
            raise ForbiddenError
        item = await use_case.execute(item_id=IntId(pk), only_published=only_published)
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(schema=item)

    @put(
        "/items/detail/{pk:int}",
        description="Обновление вопроса в матрице компетенций.",
        guards=[admin_user_guard],
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_competency_matrix_item(
        self,
        pk: int,
        resource_id_generator: FromDishka[ResourceIdGenerator],
        data: Annotated[CompetencyMatrixItemRequestSchema, Body()],
        use_case: FromDishka[AbstractUpsertItemUseCase],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.execute(
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
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_competency_matrix_item(
        self,
        pk: int,
        use_case: FromDishka[AbstractDeleteItemUseCase],
    ) -> None:
        await use_case.execute(item_id=IntId(pk))

    @post(
        "/items/detail/{pk:int}/set-draft",
        description='Установка статуса "Черновик" на вопрос в матрице компетенций.',
        guards=[admin_user_guard],
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_draft_status_to_competency_matrix_item(
        self,
        pk: int,
        use_case: FromDishka[AbstractPublishSwitchItemUseCase],
    ) -> None:
        await use_case.execute(item_id=IntId(pk), publish_status=PublishStatusEnum.DRAFT)

    @post(
        "/items/detail/{pk:int}/set-published",
        description='Установка статуса "Опубликовано" на вопрос в матрице компетенций.',
        guards=[admin_user_guard],
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def set_published_status_to_competency_matrix_item(
        self,
        pk: int,
        use_case: FromDishka[AbstractPublishSwitchItemUseCase],
    ) -> None:
        await use_case.execute(item_id=IntId(pk), publish_status=PublishStatusEnum.PUBLISHED)


api_router = DishkaRouter("", route_handlers=[CompetencyMatrixApiController])
