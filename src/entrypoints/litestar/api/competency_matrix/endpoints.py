from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import get
from litestar.params import Parameter

from config.settings import settings
from core.competency_matrix.use_cases import (
    AbstractGetItemUseCase,
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
)
from entrypoints.litestar.api.competency_matrix.schemas import (
    CompetencyMatrixItemDetailSchema,
    CompetencyMatrixItemsListSchema,
    CompetencyMatrixSheetsListSchema,
)


@get(
    "/items",
    description="Получение списка вопросов по матрице компетенций.",
    cache=settings.app.get_cache_duration(60),  # 1 минута
)
async def list_competency_matrix_items_handler(
    sheet_name: Annotated[str, Parameter(query="sheetName")],
    use_case: FromDishka[AbstractListItemsUseCase],
) -> CompetencyMatrixItemsListSchema:
    items = await use_case.execute(sheet_name=sheet_name)
    return CompetencyMatrixItemsListSchema.from_domain_schema(sheet=sheet_name, schema=items)


@get(
    "/items/{pk:int}",
    description="Получение подробной информации о вопросе из матрицы компетенций.",
    cache=settings.app.get_cache_duration(15),  # 15 секунд
)
async def get_competency_matrix_item_handler(
    pk: int,
    use_case: FromDishka[AbstractGetItemUseCase],
) -> CompetencyMatrixItemDetailSchema:
    item = await use_case.execute(item_id=pk)
    return CompetencyMatrixItemDetailSchema.from_domain_schema(schema=item)


@get(
    "/sheets",
    description=(
        "Получение списка листов матрицы компетенций. Список содержит только доступные листы "
        "без вывода вопросов по ним. Сделайте запрос на ручку `items/` с параметром sheetId, "
        "чтобы получить вопросы по нужному листу."
    ),
    cache=settings.app.get_cache_duration(120),  # 2 минуты
)
async def list_competency_matrix_sheet_handler(
    use_case: FromDishka[AbstractListSheetsUseCase],
) -> CompetencyMatrixSheetsListSchema:
    sheets = await use_case.execute()
    return CompetencyMatrixSheetsListSchema.from_domain_schema(schema=sheets)


api_router = DishkaRouter(
    "/competency-matrix",
    route_handlers=[
        list_competency_matrix_items_handler,
        get_competency_matrix_item_handler,
        list_competency_matrix_sheet_handler,
    ],
)
