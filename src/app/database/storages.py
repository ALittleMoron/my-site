from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.competency_matrix.schemas import Sheet, ShortCompetencyMatrixItem, Subsection
from app.database.models import CompetencyMatrixItemModel, SectionModel, SheetModel, SubsectionModel


class CompetencyMatrixStorage(ABC):
    @abstractmethod
    async def list_competency_matrix_items(
        self,
        sheet_id: int | None = None,
    ) -> list[ShortCompetencyMatrixItem]:
        raise NotImplementedError

    @abstractmethod
    async def list_sheets(self) -> list[Sheet]:
        raise NotImplementedError

    @abstractmethod
    async def list_subsections(self) -> list[Subsection]:
        raise NotImplementedError


@dataclass
class DatabaseStorage(CompetencyMatrixStorage):
    session: AsyncSession

    async def list_competency_matrix_items(
        self,
        sheet_id: int | None = None,
    ) -> list[ShortCompetencyMatrixItem]:
        query = select(CompetencyMatrixItemModel)
        if sheet_id is not None:
            query = (
                query.join(
                    SubsectionModel,
                    SubsectionModel.id == CompetencyMatrixItemModel.subsection_id,
                )
                .join(SectionModel, SectionModel.id == SubsectionModel.section_id)
                .join(SheetModel, SheetModel.id == SectionModel.sheet_id)
                .where(SheetModel.id == sheet_id)
            )
        return [item.to_short_domain_schema() for item in await self.session.scalars(query)]

    async def list_sheets(self) -> list[Sheet]:
        query = select(SheetModel)
        return [sheet.to_schema() for sheet in await self.session.scalars(query)]

    async def list_subsections(self) -> list[Subsection]:
        query = select(SubsectionModel).options(
            joinedload(SubsectionModel.section).joinedload(SectionModel.sheet),
        )
        return [subsection.to_full_schema() for subsection in await self.session.scalars(query)]
