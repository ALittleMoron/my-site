from abc import ABC, abstractmethod

from core.competency_matrix.schemas import CompetencyMatrixItem


class CompetencyMatrixStorage(ABC):
    @abstractmethod
    async def list_sheets(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def list_subsections(self, sheet_name: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def list_competency_matrix_items(self, sheet_name: str) -> list[CompetencyMatrixItem]:
        pass


class CompetencyMatrixDatabaseStorage(CompetencyMatrixStorage):
    async def list_sheets(self) -> list[str]:
        return []

    async def list_subsections(self, sheet_name: str) -> list[str]:
        _ = sheet_name
        return []

    async def list_competency_matrix_items(self, sheet_name: str) -> list[CompetencyMatrixItem]:
        _ = sheet_name
        return []
