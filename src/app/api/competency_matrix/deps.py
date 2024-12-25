from typing import Annotated

from litestar.params import Dependency, Parameter

from app.api.competency_matrix.schemas import (
    CompetencyMatrixListItemsParams,
    CompetencyMatrixListSubsectionsParams,
)
from app.core.competency_matrix.use_cases import (
    GetItemUseCase,
    ListItemsUseCase,
    ListSheetsUseCase,
    ListSubsectionsUseCase,
)
from app.database.storages import CompetencyMatrixStorage

no_validation_dependency = Dependency(skip_validation=True)


async def build_list_items_use_case(storage: CompetencyMatrixStorage) -> ListItemsUseCase:
    return ListItemsUseCase(storage=storage)


ListItemsUseCaseDeps = Annotated[ListItemsUseCase, no_validation_dependency]


async def build_get_item_use_case(storage: CompetencyMatrixStorage) -> GetItemUseCase:
    return GetItemUseCase(storage=storage)


GetItemUseCaseDeps = Annotated[GetItemUseCase, no_validation_dependency]


async def build_list_sheets_use_case(storage: CompetencyMatrixStorage) -> ListSheetsUseCase:
    return ListSheetsUseCase(storage=storage)


ListSheetsUseCaseDeps = Annotated[ListSheetsUseCase, no_validation_dependency]


async def build_list_subsections_use_case(
    storage: CompetencyMatrixStorage,
) -> ListSubsectionsUseCase:
    return ListSubsectionsUseCase(storage=storage)


ListSubsectionsUseCaseDeps = Annotated[
    ListSubsectionsUseCase,
    no_validation_dependency,
]


async def build_items_params(
    sheet_id: Annotated[
        int,
        Parameter(
            int,
            required=True,
            title="Идентификатор",
            description="Идентификатор листа, на котором располагаются вопросы",
            query="sheetId",
        ),
    ],
) -> CompetencyMatrixListItemsParams:
    return CompetencyMatrixListItemsParams(sheet_id=sheet_id)


async def build_subsections_params(
    sheet_id: Annotated[
        int,
        Parameter(
            int,
            required=True,
            title="Идентификатор",
            description="Идентификатор листа, на котором располагаются подразделы",
            query="sheetId",
        ),
    ],
) -> CompetencyMatrixListSubsectionsParams:
    return CompetencyMatrixListSubsectionsParams(sheet_id=sheet_id)
