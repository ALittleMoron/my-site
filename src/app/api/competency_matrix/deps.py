from typing import Annotated

from litestar.di import Provide
from litestar.openapi.spec import Example
from litestar.params import Dependency, Parameter

from app.api.competency_matrix.schemas import CompetencyMatrixListItemsParams
from app.core.competency_matrix.use_cases import ListCompetencyMatrixItemsUseCase
from app.database.storages import CompetencyMatrixStorage


async def list_competency_matrix_items_use_case_deps(
    storage: CompetencyMatrixStorage,
) -> ListCompetencyMatrixItemsUseCase:
    return ListCompetencyMatrixItemsUseCase(storage=storage)


ListCompetencyMatrixItemsUseCaseDeps = Annotated[
    ListCompetencyMatrixItemsUseCase,
    Dependency(skip_validation=True),
]


async def build_competency_matrix_list_items_params(
    sheetId: Annotated[
        int | None,
        Parameter(
            title="Идентификатор",
            description="Идентификатор листа, на котором располагаются вопросы",
            examples=[
                Example(
                    summary="Любое число",
                    description=(
                        "Любой числовой идентификатор листа с вопросами. "
                        "Если числа нет в базе, то выдаст пустой список."
                    ),
                    value=1,
                ),
            ],
        ),
    ] = None,
) -> CompetencyMatrixListItemsParams:
    return CompetencyMatrixListItemsParams(sheet_id=sheetId)


dependencies = {
    "list_competency_matrix_items_params": Provide(build_competency_matrix_list_items_params),
    "list_competency_matrix_items_use_case": Provide(
        list_competency_matrix_items_use_case_deps,
    ),
}
