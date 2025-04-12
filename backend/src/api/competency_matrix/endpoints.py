import anydi
from django.http import HttpRequest
from ninja import Query, Router
from verbose_http_exceptions import status

from api.competency_matrix.schemas import (
    CompetencyMatrixItemDetailSchema,
    CompetencyMatrixItemsListSchema,
    CompetencyMatrixListItemsParams,
    CompetencyMatrixSheetsListSchema,
)
from core.competency_matrix.use_cases import (
    GetItemUseCase,
    ListItemsUseCase,
    ListSheetsUseCase,
)

router = Router(tags=["competency matrix"])


@router.get(
    "items/",
    response={status.HTTP_200_OK: CompetencyMatrixItemsListSchema},
    description="Получение списка вопросов по матрице компетенций.",
    by_alias=True,
)
async def list_competency_matrix_items_handler(
    request: HttpRequest,
    params: Query[CompetencyMatrixListItemsParams],
    use_case: ListItemsUseCase = anydi.auto,
) -> CompetencyMatrixItemsListSchema:
    items = await use_case.execute(sheet_name=params.sheet_name)
    return CompetencyMatrixItemsListSchema.from_domain_schema(
        sheet=params.sheet_name,
        schema=items,
    )


@router.get(
    "items/{pk}/",
    response={status.HTTP_200_OK: CompetencyMatrixItemDetailSchema},
    description="Получение подробной информации о вопросе из матрицы компетенций.",
    by_alias=True,
)
async def get_competency_matrix_item_handler(
    request: HttpRequest,
    pk: int,
    use_case: GetItemUseCase = anydi.auto,
) -> CompetencyMatrixItemDetailSchema:
    item = await use_case.execute(item_id=pk)
    return CompetencyMatrixItemDetailSchema.from_domain_schema(
        schema=item,
    )


@router.get(
    "sheets/",
    response={status.HTTP_200_OK: CompetencyMatrixSheetsListSchema},
    description=(
        "Получение списка листов матрицы компетенций. Список содержит только доступные листы "
        "без вывода вопросов по ним. Сделайте запрос на ручку `items/` с параметром sheetId, "
        "чтобы получить вопросы по нужному листу."
    ),
    by_alias=True,
)
async def list_competency_matrix_sheet_handler(
    request: HttpRequest,
    use_case: ListSheetsUseCase = anydi.auto,
) -> CompetencyMatrixSheetsListSchema:
    sheets = await use_case.execute()
    return CompetencyMatrixSheetsListSchema.from_domain_schema(schema=sheets)
