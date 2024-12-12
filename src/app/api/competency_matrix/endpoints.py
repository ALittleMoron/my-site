from litestar import MediaType, Router, get, status_codes

from app.api.competency_matrix.deps import (
    ListCompetencyMatrixItemsUseCaseDeps,
    ListCompetencyMatrixSheetsUseCaseDeps,
    ListCompetencyMatrixSubsectionsUseCaseDeps,
)
from app.api.competency_matrix.schemas import (
    CompetencyMatrixItemsListSchema,
    CompetencyMatrixListItemsParams,
    CompetencyMatrixListSubsectionsParams,
    CompetencyMatrixSheetsListSchema,
    CompetencyMatrixSubsectionsListSchema,
)


@get(
    "items/",
    media_type=MediaType.JSON,
    status_code=status_codes.HTTP_200_OK,
    description="Получение списка вопросов по матрице компетенций.",
)
async def list_competency_matrix_items_handler(
    list_competency_matrix_items_params: CompetencyMatrixListItemsParams,
    list_competency_matrix_items_use_case: ListCompetencyMatrixItemsUseCaseDeps,
) -> CompetencyMatrixItemsListSchema:
    params = list_competency_matrix_items_params.to_schema()
    matrix = await list_competency_matrix_items_use_case.execute(params=params)
    return CompetencyMatrixItemsListSchema.from_domain_schema(schema=matrix)


@get(
    "sheets/",
    media_type=MediaType.JSON,
    status_code=status_codes.HTTP_200_OK,
    description=(
        "Получение списка листов матрицы компетенций. Список содержит только доступные листы "
        "без вывода вопросов по ним. Сделайте запрос на ручку `items/` с параметром sheetId, "
        "чтобы получить вопросы по нужному листу."
    ),
)
async def list_competency_matrix_sheet_handler(
    list_competency_matrix_sheets_use_case: ListCompetencyMatrixSheetsUseCaseDeps,
) -> CompetencyMatrixSheetsListSchema:
    sheets = await list_competency_matrix_sheets_use_case.execute()
    return CompetencyMatrixSheetsListSchema.from_domain_schema(schema=sheets)


@get(
    "subsections/",
    media_type=MediaType.JSON,
    status_code=status_codes.HTTP_200_OK,
    description=(
        "Получение списка подразделов листов матрицы компетенций. Также в ответе содержится "
        "информация о разделе и листе данных подразделов."
    ),
)
async def list_competency_matrix_subsection_handler(
    list_competency_matrix_subsections_params: CompetencyMatrixListSubsectionsParams,
    list_competency_matrix_subsections_use_case: ListCompetencyMatrixSubsectionsUseCaseDeps,
) -> CompetencyMatrixSubsectionsListSchema:
    params = list_competency_matrix_subsections_params.to_schema()
    subsections = await list_competency_matrix_subsections_use_case.execute(params=params)
    return CompetencyMatrixSubsectionsListSchema.from_domain_schema(schema=subsections)


router = Router(
    "/competencyMatrix/",
    route_handlers=[
        list_competency_matrix_items_handler,
        list_competency_matrix_sheet_handler,
        list_competency_matrix_subsection_handler,
    ],
    tags=["competency matrix"],
)
