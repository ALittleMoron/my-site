from typing import Annotated

from litestar import MediaType, Router, get, status_codes
from litestar.di import Provide
from litestar.params import Parameter

from app.api.competency_matrix.deps import (
    GetItemUseCaseDeps,
    ListItemsUseCaseDeps,
    ListSheetsUseCaseDeps,
    ListSubsectionsUseCaseDeps,
    build_get_item_use_case,
    build_items_params,
    build_list_items_use_case,
    build_list_sheets_use_case,
    build_list_subsections_use_case,
    build_subsections_params,
)
from app.api.competency_matrix.schemas import (
    CompetencyMatrixItemDetailSchema,
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
    dependencies={
        'params': Provide(build_items_params),
        "use_case": Provide(build_list_items_use_case),
    },
    description="Получение списка вопросов по матрице компетенций.",
)
async def list_competency_matrix_items_handler(
    params: CompetencyMatrixListItemsParams,
    use_case: ListItemsUseCaseDeps,
) -> CompetencyMatrixItemsListSchema:
    matrix = await use_case.execute(params=params.to_schema())
    return CompetencyMatrixItemsListSchema.from_domain_schema(schema=matrix)


@get(
    "items/{pk:int}/",
    media_type=MediaType.JSON,
    status_code=status_codes.HTTP_200_OK,
    dependencies={"use_case": Provide(build_get_item_use_case)},
    description="Получение списка вопросов по матрице компетенций.",
)
async def detail_competency_matrix_items_handler(
    pk: Annotated[int, Parameter(int, description="Идентификатор вопроса")],
    use_case: GetItemUseCaseDeps,
) -> CompetencyMatrixItemDetailSchema:
    item = await use_case.execute(item_id=pk)
    return CompetencyMatrixItemDetailSchema.from_domain_schema(schema=item)


@get(
    "sheets/",
    media_type=MediaType.JSON,
    status_code=status_codes.HTTP_200_OK,
    dependencies={"use_case": Provide(build_list_sheets_use_case)},
    description=(
        "Получение списка листов матрицы компетенций. Список содержит только доступные листы "
        "без вывода вопросов по ним. Сделайте запрос на ручку `items/` с параметром sheetId, "
        "чтобы получить вопросы по нужному листу."
    ),
)
async def list_competency_matrix_sheet_handler(
    use_case: ListSheetsUseCaseDeps,
) -> CompetencyMatrixSheetsListSchema:
    sheets = await use_case.execute()
    return CompetencyMatrixSheetsListSchema.from_domain_schema(schema=sheets)


@get(
    "subsections/",
    media_type=MediaType.JSON,
    status_code=status_codes.HTTP_200_OK,
    dependencies={
        "params": Provide(build_subsections_params),
        "use_case": Provide(build_list_subsections_use_case),
    },
    description=(
        "Получение списка подразделов листов матрицы компетенций. Также в ответе содержится "
        "информация о разделе и листе данных подразделов."
    ),
)
async def list_competency_matrix_subsection_handler(
    params: CompetencyMatrixListSubsectionsParams,
    use_case: ListSubsectionsUseCaseDeps,
) -> CompetencyMatrixSubsectionsListSchema:
    subsections = await use_case.execute(params=params.to_schema())
    return CompetencyMatrixSubsectionsListSchema.from_domain_schema(schema=subsections)


router = Router(
    "/competencyMatrix/",
    route_handlers=[
        list_competency_matrix_items_handler,
        detail_competency_matrix_items_handler,
        list_competency_matrix_sheet_handler,
        list_competency_matrix_subsection_handler,
    ],
    tags=["competency matrix"],
)
