from litestar import MediaType, Router, get, status_codes

from app.api.competency_matrix.deps import ListCompetencyMatrixItemsUseCaseDeps
from app.api.competency_matrix.schemas import CompetencyMatrixListSchema


@get(
    "items/",
    media_type=MediaType.JSON,
    status_code=status_codes.HTTP_200_OK,
    description="Получение списка вопросов по матрице компетенций.",
)
async def list_competency_matrix_handler(
    list_competency_matrix_items_use_case: ListCompetencyMatrixItemsUseCaseDeps,
) -> CompetencyMatrixListSchema:
    matrix = await list_competency_matrix_items_use_case.execute()
    return CompetencyMatrixListSchema.from_domain_schema(schema=matrix)


router = Router(
    "/competencyMatrix/",
    route_handlers=[list_competency_matrix_handler],
    tags=["competency matrix"],
)
