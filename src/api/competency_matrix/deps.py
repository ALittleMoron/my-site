import anydi

from core.competency_matrix.use_cases import (
    ListItemsUseCase,
    ListSheetsUseCase,
)
from db.storages import CompetencyMatrixStorage


class CompetencyMatrixDepsModule(anydi.Module):
    @anydi.provider(scope="singleton")
    async def build_list_items_use_case(
        self,
        storage: CompetencyMatrixStorage = anydi.auto,
    ) -> ListItemsUseCase:
        return ListItemsUseCase(storage=storage)

    @anydi.provider(scope="singleton")
    async def build_list_sheets_use_case(
        self,
        storage: CompetencyMatrixStorage = anydi.auto,
    ) -> ListSheetsUseCase:
        return ListSheetsUseCase(storage=storage)
