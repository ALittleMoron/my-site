from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from core.competency_matrix.schemas import CompetencyMatrixItem
from db.models import CompetencyMatrixItemModel


@dataclass(kw_only=True)
class StorageHelper:
    session: AsyncSession

    async def create_competency_matrix_item(
        self,
        item: CompetencyMatrixItem,
    ) -> CompetencyMatrixItemModel:
        model = CompetencyMatrixItemModel.from_domain_schema(item=item)
        await self.session.merge(model)
        return model

    async def create_competency_matrix_items(
        self,
        items: list[CompetencyMatrixItem],
    ) -> list[CompetencyMatrixItemModel]:
        items = [CompetencyMatrixItemModel.from_domain_schema(item=item) for item in items]
        self.session.add_all(items)
        await self.session.commit()
        return items
