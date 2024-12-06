from typing import Annotated

from litestar.di import Provide
from litestar.params import Dependency

from app.core.competency_matrix.use_cases import ListCompetencyMatrixItemsUseCase
from app.database.storage import Storage


async def list_competency_matrix_items_use_case_deps(
    storage: Storage,
) -> ListCompetencyMatrixItemsUseCase:
    return ListCompetencyMatrixItemsUseCase(storage=storage)


ListCompetencyMatrixItemsUseCaseDeps = Annotated[
    ListCompetencyMatrixItemsUseCase,
    Dependency(skip_validation=True),
]


dependencies = {
    "list_competency_matrix_items_use_case": Provide(
        list_competency_matrix_items_use_case_deps,
    ),
}
