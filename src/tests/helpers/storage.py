from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.competency_matrix.schemas import FullCompetencyMatrixItem
from app.database.models import CompetencyMatrixItemModel


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
