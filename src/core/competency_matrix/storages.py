from abc import ABC, abstractmethod

from core.competency_matrix.schemas import CompetencyMatrixItem


class CompetencyMatrixStorage(ABC):
    @abstractmethod
    async def list_sheets(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def list_competency_matrix_items(self, sheet_name: str) -> list[CompetencyMatrixItem]:
        raise NotImplementedError

    @abstractmethod
    async def get_competency_matrix_item(self, item_id: int) -> CompetencyMatrixItem:
        raise NotImplementedError
