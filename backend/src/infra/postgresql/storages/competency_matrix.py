from dataclasses import dataclass

from sqlalchemy import ARRAY, Integer, bindparam, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.schemas import CompetencyMatrixItem, ExternalResources, Sheet, Sheets
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import IntId
from infra.postgresql.models import CompetencyMatrixItemModel, ExternalResourceModel
from infra.postgresql.models.competency_matrix import ResourceToItemSecondaryModel


@dataclass(kw_only=True)
class CompetencyMatrixDatabaseStorage(CompetencyMatrixStorage):
    session: AsyncSession

    async def list_sheets(self) -> Sheets:
        stmt = (
            select(
                CompetencyMatrixItemModel.sheet_key,
                CompetencyMatrixItemModel.sheet_ru,
                CompetencyMatrixItemModel.sheet_en,
            )
            .where(CompetencyMatrixItemModel.publish_status == PublishStatusEnum.PUBLISHED)
            .distinct()
            .order_by(CompetencyMatrixItemModel.sheet_key)
        )
        rows = await self.session.execute(stmt)
        return Sheets(
            values=[
                Sheet(key=row.sheet_key, name_ru=row.sheet_ru, name_en=row.sheet_en) for row in rows
            ],
        )

    async def list_competency_matrix_items(self, sheet_key: str) -> list[CompetencyMatrixItem]:
        stmt = (
            select(CompetencyMatrixItemModel)
            .where(func.lower(CompetencyMatrixItemModel.sheet_key) == sheet_key.lower())
            .order_by(
                CompetencyMatrixItemModel.section_en,
                CompetencyMatrixItemModel.subsection_en,
                CompetencyMatrixItemModel.grade,
                CompetencyMatrixItemModel.id,
            )
        )
        items = await self.session.scalars(stmt)
        return [item.to_domain_schema(include_relationships=False) for item in items]

    async def get_competency_matrix_item(self, item_id: IntId) -> CompetencyMatrixItem:
        stmt = (
            select(CompetencyMatrixItemModel)
            .where(CompetencyMatrixItemModel.id == item_id)
            .options(
                selectinload(CompetencyMatrixItemModel.resource_links).selectinload(
                    ResourceToItemSecondaryModel.resource,
                ),
            )
        )
        item = await self.session.scalar(stmt)
        if item is None:
            raise CompetencyMatrixItemNotFoundError
        return item.to_domain_schema(include_relationships=True)

    async def create_competency_matrix_item(
        self,
        item: CompetencyMatrixItem,
    ) -> CompetencyMatrixItem:
        item_model = CompetencyMatrixItemModel.from_domain_schema(
            item=item,
            include_relationships=False,
        )
        item_model.resource_links = await self._build_resource_links(
            item=item,
            existing_links=None,
        )
        self.session.add(item_model)
        await self.session.flush()
        return await self.get_competency_matrix_item(item_id=item.id)

    async def update_competency_matrix_item(
        self,
        item: CompetencyMatrixItem,
    ) -> CompetencyMatrixItem:
        item_model = await self._get_competency_matrix_item_model(
            item_id=item.id,
            load_resource_links=True,
        )
        item_model.update_from_domain_schema(item=item)
        item_model.resource_links = await self._build_resource_links(
            item=item,
            existing_links=item_model.resource_links,
        )
        await self.session.flush()
        return await self.get_competency_matrix_item(item_id=item.id)

    async def update_competency_matrix_item_publish_status(
        self,
        item_id: IntId,
        publish_status: PublishStatusEnum,
    ) -> None:
        item_model = await self._get_competency_matrix_item_model(
            item_id=item_id,
            load_resource_links=False,
        )
        item_model.publish_status = publish_status
        await self.session.flush()

    async def _get_competency_matrix_item_model(
        self,
        item_id: IntId,
        *,
        load_resource_links: bool,
    ) -> CompetencyMatrixItemModel:
        stmt = select(CompetencyMatrixItemModel).where(CompetencyMatrixItemModel.id == item_id)
        if load_resource_links:
            stmt = stmt.options(selectinload(CompetencyMatrixItemModel.resource_links))
        item_model = await self.session.scalar(stmt)
        if item_model is None:
            raise CompetencyMatrixItemNotFoundError
        return item_model

    async def _build_resource_links(
        self,
        item: CompetencyMatrixItem,
        existing_links: list[ResourceToItemSecondaryModel] | None,
    ) -> list[ResourceToItemSecondaryModel]:
        links: list[ResourceToItemSecondaryModel] = []
        existing_links_by_resource_id = {link.resource_id: link for link in existing_links or []}
        for resource in item.resources:
            resource_model = await self.session.merge(
                ExternalResourceModel.from_domain_schema(
                    schema=resource.to_external_resource(),
                ),
            )
            link = existing_links_by_resource_id.get(resource.id)
            if link is None:
                link = ResourceToItemSecondaryModel(resource_id=resource.id)
            link.resource = resource_model
            link.context_ru = resource.context_ru
            link.context_en = resource.context_en
            links.append(link)
        return links

    async def get_resources_by_ids(
        self,
        resource_ids: list[IntId],
    ) -> ExternalResources:
        ids = bindparam("ids", value=resource_ids, type_=ARRAY(Integer))
        cte = select(func.unnest(ids).label("resource_id")).cte("ids")
        stmt = select(ExternalResourceModel).join(
            cte,
            ExternalResourceModel.id == cte.c.resource_id,
        )
        resources = await self.session.scalars(stmt)
        return ExternalResources(values=[resource.to_domain_schema() for resource in resources])

    async def delete_competency_matrix_item(self, item_id: IntId) -> None:
        stmt = select(CompetencyMatrixItemModel).where(CompetencyMatrixItemModel.id == item_id)
        item = await self.session.scalar(stmt)
        if item is None:
            raise CompetencyMatrixItemNotFoundError
        await self.session.delete(item)
        await self.session.flush()

    async def search_competency_matrix_resources(
        self,
        search_name: str,
        limit: int,
        language: LanguageEnum,
    ) -> ExternalResources:
        lowered_search_name = search_name.lower()
        name_column = self._resource_name_column(language=language)
        stmt = (
            select(ExternalResourceModel)
            .where(
                or_(
                    func.lower(name_column).ilike(f"%{lowered_search_name}%"),
                    func.lower(ExternalResourceModel.url).ilike(f"%{lowered_search_name}%"),
                ),
            )
            .order_by(
                case(
                    (func.lower(name_column) == lowered_search_name, 0),
                    (func.lower(name_column).startswith(lowered_search_name), 1),
                    else_=2,
                ),
                name_column,
            )
            .limit(limit)
        )
        resources = await self.session.scalars(stmt)
        return ExternalResources(values=[resource.to_domain_schema() for resource in resources])

    def _resource_name_column(
        self,
        *,
        language: LanguageEnum,
    ) -> InstrumentedAttribute[str]:
        if language == LanguageEnum.RU:
            return ExternalResourceModel.name_ru
        return ExternalResourceModel.name_en
