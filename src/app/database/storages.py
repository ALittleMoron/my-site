from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.competency_matrix.schemas import ShortCompetencyMatrixItem
from app.database.models import CompetencyMatrixItemModel


class CompetencyMatrixStorage(ABC):
    @abstractmethod
    async def list_competency_matrix_items(self) -> list[ShortCompetencyMatrixItem]:
        raise NotImplementedError


@dataclass
class DatabaseStorage(CompetencyMatrixStorage):
    session: AsyncSession

    async def list_competency_matrix_items(self) -> list[ShortCompetencyMatrixItem]:
        query = select(CompetencyMatrixItemModel)
        return [item.to_short_domain_schema() for item in await self.session.scalars(query)]
