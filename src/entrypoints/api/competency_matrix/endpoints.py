from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query

from core.competency_matrix.use_cases import (
    AbstractGetItemUseCase,
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
)
from entrypoints.api.competency_matrix.schemas import (
    CompetencyMatrixItemDetailSchema,
    CompetencyMatrixItemsListSchema,
    CompetencyMatrixListItemsParams,
    CompetencyMatrixSheetsListSchema,
)

api_router = APIRouter()


@api_router.get(
    "/competency-matrix/items",
    description="Получение списка вопросов по матрице компетенций.",
)
@inject
async def list_competency_matrix_items_handler(
    params: Annotated[CompetencyMatrixListItemsParams, Query()],
    use_case: FromDishka[AbstractListItemsUseCase],
) -> CompetencyMatrixItemsListSchema:
    items = await use_case.execute(sheet_name=params.sheet_name)
    return CompetencyMatrixItemsListSchema.from_domain_schema(
        sheet=params.sheet_name,
        schema=items,
    )


@api_router.get(
    "/competency-matrix/items/{pk}",
    description="Получение подробной информации о вопросе из матрицы компетенций.",
)
@inject
async def get_competency_matrix_item_handler(
    pk: int,
    use_case: FromDishka[AbstractGetItemUseCase],
) -> CompetencyMatrixItemDetailSchema:
    item = await use_case.execute(item_id=pk)
    return CompetencyMatrixItemDetailSchema.from_domain_schema(
        schema=item,
    )


@api_router.get(
    "/competency-matrix/sheets",
    description=(
        "Получение списка листов матрицы компетенций. Список содержит только доступные листы "
        "без вывода вопросов по ним. Сделайте запрос на ручку `items/` с параметром sheetId, "
        "чтобы получить вопросы по нужному листу."
    ),
)
@inject
async def list_competency_matrix_sheet_handler(
    use_case: FromDishka[AbstractListSheetsUseCase],
) -> CompetencyMatrixSheetsListSchema:
    sheets = await use_case.execute()
    return CompetencyMatrixSheetsListSchema.from_domain_schema(schema=sheets)
