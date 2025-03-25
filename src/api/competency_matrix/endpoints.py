import anydi
from django.http import HttpRequest
from ninja import Query, Router
from verbose_http_exceptions import status

from api.competency_matrix.schemas import (
    CompetencyMatrixItemsListSchema,
    CompetencyMatrixListItemsParams,
    CompetencyMatrixSheetsListSchema,
)
from core.competency_matrix.use_cases import (
    ListItemsUseCase,
    ListSheetsUseCase,
)

router = Router(
    tags=["competency matrix"],
)


@router.get(
    "items/",
    response={status.HTTP_200_OK: CompetencyMatrixItemsListSchema},
    description="Получение списка вопросов по матрице компетенций.",
)
async def list_competency_matrix_items_handler(
    request: HttpRequest,  # noqa
    params: Query[CompetencyMatrixListItemsParams],
    use_case: ListItemsUseCase = anydi.auto,
) -> CompetencyMatrixItemsListSchema:
    matrix = await use_case.execute(sheet_name=params.sheet_name)
    return CompetencyMatrixItemsListSchema.from_domain_schema(schema=matrix)


@router.get(
    "sheets/",
    response={status.HTTP_200_OK: CompetencyMatrixSheetsListSchema},
    description=(
        "Получение списка листов матрицы компетенций. Список содержит только доступные листы "
        "без вывода вопросов по ним. Сделайте запрос на ручку `items/` с параметром sheetId, "
        "чтобы получить вопросы по нужному листу."
    ),
)
async def list_competency_matrix_sheet_handler(
    request: HttpRequest,  # noqa
    use_case: ListSheetsUseCase = anydi.auto,
) -> CompetencyMatrixSheetsListSchema:
    sheets = await use_case.execute()
    return CompetencyMatrixSheetsListSchema.from_domain_schema(schema=sheets)
