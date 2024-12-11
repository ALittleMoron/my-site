from typing import Annotated

from litestar.di import Provide
from litestar.params import Dependency, Parameter

from app.api.competency_matrix.schemas import (
    CompetencyMatrixListItemsParams,
    CompetencyMatrixListSubsectionsParams,
)
from app.core.competency_matrix.use_cases import (
    ListCompetencyMatrixItemsUseCase,
    ListSheetsUseCase,
    ListSubsectionsUseCase,
)
from app.database.storages import CompetencyMatrixStorage


async def list_competency_matrix_items_use_case_deps(
    storage: CompetencyMatrixStorage,
) -> ListCompetencyMatrixItemsUseCase:
    return ListCompetencyMatrixItemsUseCase(storage=storage)


ListCompetencyMatrixItemsUseCaseDeps = Annotated[
    ListCompetencyMatrixItemsUseCase,
    Dependency(skip_validation=True),
]


async def list_competency_matrix_sheets_use_case_deps(
    storage: CompetencyMatrixStorage,
) -> ListSheetsUseCase:
    return ListSheetsUseCase(storage=storage)


ListCompetencyMatrixSheetsUseCaseDeps = Annotated[
    ListSheetsUseCase,
    Dependency(skip_validation=True),
]


async def list_competency_matrix_subsections_use_case_deps(
    storage: CompetencyMatrixStorage,
) -> ListSubsectionsUseCase:
    return ListSubsectionsUseCase(storage=storage)


ListCompetencyMatrixSubsectionsUseCaseDeps = Annotated[
    ListSubsectionsUseCase,
    Dependency(skip_validation=True),
]


async def build_competency_matrix_list_items_params(
    sheet_id: Annotated[
        int | None,
        Parameter(
            int | None,
            title="Идентификатор",
            description="Идентификатор листа, на котором располагаются вопросы",
            query="sheetId",
        ),
    ] = None,
) -> CompetencyMatrixListItemsParams:
    return CompetencyMatrixListItemsParams(sheet_id=sheet_id)


async def build_competency_matrix_subsections_params(
    sheet_id: Annotated[
        int | None,
        Parameter(
            int | None,
            title="Идентификатор",
            description="Идентификатор листа, на котором располагаются подразделы",
            query="sheetId",
        ),
    ] = None,
):
    return CompetencyMatrixListSubsectionsParams(sheet_id=sheet_id)


dependencies = {
    "list_competency_matrix_items_params": Provide(build_competency_matrix_list_items_params),
    "list_competency_matrix_subsections_params": Provide(
        build_competency_matrix_subsections_params
    ),
    "list_competency_matrix_items_use_case": Provide(
        list_competency_matrix_items_use_case_deps,
    ),
    "list_competency_matrix_sheets_use_case": Provide(
        list_competency_matrix_sheets_use_case_deps,
    ),
    "list_competency_matrix_subsections_use_case": Provide(
        list_competency_matrix_subsections_use_case_deps,
    ),
}
