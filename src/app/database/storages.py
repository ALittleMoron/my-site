from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from app.core.competency_matrix.schemas import (
    FullCompetencyMatrixItem,
    Sheet,
    ShortCompetencyMatrixItem,
    Subsection,
)
from app.database.models import CompetencyMatrixItemModel, SectionModel, SheetModel, SubsectionModel


class CompetencyMatrixStorage(ABC):
    @abstractmethod
    async def get_competency_matrix_item(self, item_id: int) -> FullCompetencyMatrixItem:
        raise NotImplementedError

    @abstractmethod
    async def list_competency_matrix_items(
        self,
        sheet_id: int,
    ) -> list[ShortCompetencyMatrixItem]:
        raise NotImplementedError

    @abstractmethod
    async def list_sheets(self) -> list[Sheet]:
        raise NotImplementedError

    @abstractmethod
    async def list_subsections(
        self,
        sheet_id: int,
    ) -> list[Subsection]:
        raise NotImplementedError


@dataclass
class DatabaseStorage(CompetencyMatrixStorage):
    session: AsyncSession

    async def get_competency_matrix_item(self, item_id: int) -> FullCompetencyMatrixItem:
        query = (
            select(CompetencyMatrixItemModel)
            .options(
                joinedload(CompetencyMatrixItemModel.grade),
                (
                    joinedload(CompetencyMatrixItemModel.subsection)
                    .joinedload(SubsectionModel.section)
                    .joinedload(SectionModel.sheet)
                ),
                selectinload(CompetencyMatrixItemModel.resources),
            )
            .where(CompetencyMatrixItemModel.id == item_id)
        )
        item = await self.session.scalar(query)
        if item is None:
            raise CompetencyMatrixItemNotFoundError
        return item.to_full_domain_schema()

    async def list_competency_matrix_items(
        self,
        sheet_id: int,
    ) -> list[ShortCompetencyMatrixItem]:
        query = (
            select(CompetencyMatrixItemModel)
            .join(
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

    async def list_subsections(
        self,
        sheet_id: int,
    ) -> list[Subsection]:
        query = (
            select(SubsectionModel)
            .options(
                joinedload(SubsectionModel.section).joinedload(SectionModel.sheet),
            )
            .join(SectionModel, SectionModel.id == SubsectionModel.section_id)
            .join(SheetModel, SheetModel.id == SectionModel.sheet_id)
            .where(SheetModel.id == sheet_id)
        )
        return [subsection.to_full_schema() for subsection in await self.session.scalars(query)]
