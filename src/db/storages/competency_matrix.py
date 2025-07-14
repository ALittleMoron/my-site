from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.competency_matrix.enums import StatusEnum
from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.schemas import CompetencyMatrixItem
from core.competency_matrix.storages import CompetencyMatrixStorage
from db.models import CompetencyMatrixItemModel


@dataclass(kw_only=True)
class CompetencyMatrixDatabaseStorage(CompetencyMatrixStorage):
    session: AsyncSession

    async def list_sheets(self) -> list[str]:
        stmt = (
            select(CompetencyMatrixItemModel.sheet)
            .where(CompetencyMatrixItemModel.status == StatusEnum.PUBLISHED)
            .distinct()
            .order_by(CompetencyMatrixItemModel.sheet)
        )
        sheets = await self.session.scalars(stmt)
        return list(sheets)

    async def list_competency_matrix_items(self, sheet_name: str) -> list[CompetencyMatrixItem]:
        stmt = select(CompetencyMatrixItemModel).where(
            CompetencyMatrixItemModel.status == StatusEnum.PUBLISHED,
            func.lower(CompetencyMatrixItemModel.sheet) == sheet_name.lower(),
        )
        items = await self.session.scalars(stmt)
        return [item.to_domain_schema(include_relationships=False) for item in items]

    async def get_competency_matrix_item(self, item_id: int) -> CompetencyMatrixItem:
        stmt = (
            select(CompetencyMatrixItemModel)
            .where(
                CompetencyMatrixItemModel.status == StatusEnum.PUBLISHED,
                CompetencyMatrixItemModel.id == item_id,
            )
            .options(selectinload(CompetencyMatrixItemModel.resources))
        )
        item = await self.session.scalar(stmt)
        if item is None:
            raise CompetencyMatrixItemNotFoundError
        return item.to_domain_schema(include_relationships=True)
