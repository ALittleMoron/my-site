from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import ARRAY, Integer, String, and_, bindparam, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from core.competency_matrix.exceptions import (
    CompetencyMatrixItemNotFoundError,
    QueuedCompetencyMatrixQuestionNotFoundError,
)
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItemFilters,
    ExternalResources,
    QueuedCompetencyMatrixQuestion,
    QueuedCompetencyMatrixQuestionCreateParams,
    QueuedCompetencyMatrixQuestions,
    Sheet,
    Sheets,
)
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import IntId
from infra.config.constants import constants
from infra.postgresql.models import CompetencyMatrixItemModel, ExternalResourceModel
from infra.postgresql.models.competency_matrix import (
    QueuedQuestionModel,
    ResourceToItemSecondaryModel,
)


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

    async def list_competency_matrix_items(
        self,
        *,
        filters: CompetencyMatrixItemFilters,
    ) -> list[CompetencyMatrixItem]:
        stmt = select(CompetencyMatrixItemModel).order_by(
            CompetencyMatrixItemModel.section_en,
            CompetencyMatrixItemModel.subsection_en,
            CompetencyMatrixItemModel.grade,
            CompetencyMatrixItemModel.id,
        )
        if filters.sheet_key is not None:
            stmt = stmt.where(
                func.lower(CompetencyMatrixItemModel.sheet_key) == filters.sheet_key.lower(),
            )
        if filters.only_published is True:
            stmt = stmt.where(
                CompetencyMatrixItemModel.publish_status == PublishStatusEnum.PUBLISHED,
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

    async def get_competency_matrix_item_by_slug(self, slug: str) -> CompetencyMatrixItem:
        stmt = (
            select(CompetencyMatrixItemModel)
            .where(CompetencyMatrixItemModel.slug == slug)
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
        active_name_column = self._resource_name_column(language=language)
        secondary_name_column = self._secondary_resource_name_column(language=language)
        search_query = bindparam(
            "resource_search_query",
            value=lowered_search_name,
            type_=String(),
        )
        search_pattern = f"%{lowered_search_name}%"
        prefix_pattern = f"{lowered_search_name}%"
        active_name = func.lower(active_name_column)
        secondary_name = func.lower(secondary_name_column)
        url = func.lower(ExternalResourceModel.url)
        fuzzy_search_allowed = (
            func.length(search_query) >= constants.search.min_trigram_fuzzy_query_length
        )
        similarity_score = func.greatest(
            func.similarity(active_name, search_query),
            func.similarity(secondary_name, search_query),
            func.similarity(url, search_query),
            func.word_similarity(search_query, active_name),
            func.word_similarity(search_query, secondary_name),
            func.word_similarity(search_query, url),
        )
        stmt = (
            select(ExternalResourceModel)
            .where(
                or_(
                    active_name.ilike(search_pattern),
                    secondary_name.ilike(search_pattern),
                    url.ilike(search_pattern),
                    and_(
                        fuzzy_search_allowed,
                        or_(
                            active_name.op("%")(search_query),
                            secondary_name.op("%")(search_query),
                            url.op("%")(search_query),
                            active_name.op("%>")(search_query),
                            secondary_name.op("%>")(search_query),
                            url.op("%>")(search_query),
                        ),
                    ),
                ),
            )
            .order_by(
                case(
                    (active_name == lowered_search_name, 0),
                    (active_name.like(prefix_pattern), 1),
                    (secondary_name == lowered_search_name, 2),
                    (secondary_name.like(prefix_pattern), 3),
                    (url.like(search_pattern), 4),
                    else_=5,
                ),
                similarity_score.desc(),
                active_name,
                ExternalResourceModel.id,
            )
            .limit(limit)
        )
        resources = await self.session.scalars(stmt)
        return ExternalResources(values=[resource.to_domain_schema() for resource in resources])

    async def list_queued_questions(self) -> QueuedCompetencyMatrixQuestions:
        stmt = select(QueuedQuestionModel).order_by(QueuedQuestionModel.created_at)
        questions = await self.session.scalars(stmt)
        return QueuedCompetencyMatrixQuestions(
            values=[question.to_domain_schema() for question in questions],
        )

    async def get_queued_question(self, question_id: IntId) -> QueuedCompetencyMatrixQuestion:
        question = await self._get_queued_question_model(question_id=question_id)
        return question.to_domain_schema()

    async def create_queued_question(
        self,
        *,
        params: QueuedCompetencyMatrixQuestionCreateParams,
    ) -> QueuedCompetencyMatrixQuestion:
        question = QueuedQuestionModel.from_create_params(
            params=params,
            created_at=datetime.now(tz=UTC),
        )
        self.session.add(question)
        await self.session.flush()
        return question.to_domain_schema()

    async def delete_queued_question(self, question_id: IntId) -> None:
        question = await self._get_queued_question_model(question_id=question_id)
        await self.session.delete(question)
        await self.session.flush()

    async def _get_queued_question_model(self, question_id: IntId) -> QueuedQuestionModel:
        stmt = select(QueuedQuestionModel).where(QueuedQuestionModel.id == question_id)
        question = await self.session.scalar(stmt)
        if question is None:
            raise QueuedCompetencyMatrixQuestionNotFoundError
        return question

    def _resource_name_column(
        self,
        *,
        language: LanguageEnum,
    ) -> InstrumentedAttribute[str]:
        if language == LanguageEnum.RU:
            return ExternalResourceModel.name_ru
        return ExternalResourceModel.name_en

    def _secondary_resource_name_column(
        self,
        *,
        language: LanguageEnum,
    ) -> InstrumentedAttribute[str]:
        if language == LanguageEnum.RU:
            return ExternalResourceModel.name_en
        return ExternalResourceModel.name_ru
