from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.competency_matrix.schemas import FullCompetencyMatrixItem, Sheet, Subsection
from app.database.models import CompetencyMatrixItemModel, SheetModel, SubsectionModel


@dataclass(kw_only=True)
class StorageHelper:
    session: AsyncSession
    use_flush: bool = False

    async def _flush_or_commit(self) -> None:
        await (self.session.flush() if self.use_flush else self.session.commit())

    async def insert_competency_matrix_item(
        self,
        item: FullCompetencyMatrixItem,
    ) -> CompetencyMatrixItemModel:
        db_item = CompetencyMatrixItemModel.from_domain_schema(schema=item)
        await self.session.merge(db_item)
        await self._flush_or_commit()
        return db_item

    async def insert_sheet(self, sheet: Sheet) -> SheetModel:
        db_sheet = SheetModel.from_schema(schema=sheet)
        await self.session.merge(db_sheet)
        await self._flush_or_commit()
        return db_sheet

    async def insert_subsection(self, subsection: Subsection) -> SubsectionModel:
        db_subsection = SubsectionModel.from_schema(schema=subsection)
        await self.session.merge(db_subsection)
        await self._flush_or_commit()
        return db_subsection
