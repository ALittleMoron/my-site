from dataclasses import dataclass

from core.competency_matrix.exceptions import (
    CompetencyMatrixItemNotFoundError,
    CompetencyMatrixItemNotPublicReadyError,
)
from core.competency_matrix.schemas import (
    CompetencyMatrixFilterOptions,
    CompetencyMatrixItem,
    CompetencyMatrixItemBySlugGetParams,
    CompetencyMatrixItemCreateParams,
    CompetencyMatrixItemFilters,
    CompetencyMatrixItemGetParams,
    CompetencyMatrixItemPublishStatusSwitchParams,
    CompetencyMatrixItems,
    CompetencyMatrixItemUpdateParams,
    CompetencyMatrixItemWriteParams,
    CompetencyMatrixResourceSearchParams,
    CompetencyMatrixWorkspace,
    CompetencyMatrixWorkspaceFilters,
    ExternalResources,
    PublishedCompetencyMatrixItemsForSeo,
    QuestionSuggestionCreateParams,
    QueuedCompetencyMatrixQuestion,
    QueuedCompetencyMatrixQuestionCreateItemParams,
    QueuedCompetencyMatrixQuestions,
    QueuedCompetencyMatrixQuestionsCreateParams,
    Sheets,
)
from core.competency_matrix.services import QuestionSuggestionLimiter
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import IntId


@dataclass(kw_only=True, slots=True, frozen=True)
class CompetencyMatrixUseCase:
    storage: CompetencyMatrixStorage
    question_suggestion_limiter: QuestionSuggestionLimiter

    async def list_sheets(self) -> Sheets:
        return await self.storage.list_sheets()

    async def find_resources(
        self,
        *,
        params: CompetencyMatrixResourceSearchParams,
    ) -> ExternalResources:
        return await self.storage.search_competency_matrix_resources(
            search_name=params.search_name.cleaned,
            limit=params.limit,
            language=params.language,
        )

    async def list_items(
        self,
        *,
        filters: CompetencyMatrixItemFilters,
    ) -> CompetencyMatrixItems:
        items = await self.storage.list_competency_matrix_items(filters=filters)
        matrix = CompetencyMatrixItems(values=items)
        return matrix.only_available() if filters.only_published is True else matrix

    async def get_item(
        self,
        *,
        params: CompetencyMatrixItemGetParams,
    ) -> CompetencyMatrixItem:
        item = await self.storage.get_competency_matrix_item(item_id=params.item_id)
        if params.only_published and not item.is_available():
            raise CompetencyMatrixItemNotFoundError
        return item

    async def get_item_by_slug(
        self,
        *,
        params: CompetencyMatrixItemBySlugGetParams,
    ) -> CompetencyMatrixItem:
        item = await self.storage.get_competency_matrix_item_by_slug(slug=params.slug)
        if params.only_published and not item.is_available():
            raise CompetencyMatrixItemNotFoundError
        return item

    async def list_published_items_for_seo(self) -> PublishedCompetencyMatrixItemsForSeo:
        items = await self.storage.list_competency_matrix_items(
            filters=CompetencyMatrixItemFilters(only_published=True),
        )
        return CompetencyMatrixItems(values=items).only_available().to_published_for_seo()

    async def list_workspace_items(
        self,
        *,
        filters: CompetencyMatrixWorkspaceFilters,
    ) -> CompetencyMatrixWorkspace:
        items, total_count, summary = await self.storage.list_competency_matrix_workspace_items(
            filters=filters,
        )
        return CompetencyMatrixWorkspace.from_page(
            values=items,
            total_count=total_count,
            page_size=filters.page_size,
            summary=summary,
        )

    async def list_workspace_filter_options(
        self,
        *,
        language: LanguageEnum,
    ) -> CompetencyMatrixFilterOptions:
        return await self.storage.list_competency_matrix_workspace_filter_options(
            language=language,
        )

    async def create_item(
        self,
        *,
        params: CompetencyMatrixItemCreateParams,
    ) -> CompetencyMatrixItem:
        item = await self._build_item_from_params(params=params)
        self._ensure_publishable(item=item)
        return await self.storage.create_competency_matrix_item(item=item)

    async def create_item_from_queue(
        self,
        *,
        params: QueuedCompetencyMatrixQuestionCreateItemParams,
    ) -> CompetencyMatrixItem:
        await self.storage.get_queued_question(question_id=params.queued_question_id)
        item = await self._build_item_from_params(params=params.item)
        self._ensure_publishable(item=item)
        created_item = await self.storage.create_competency_matrix_item(item=item)
        await self.storage.delete_queued_question(question_id=params.queued_question_id)
        return created_item

    async def update_item(
        self,
        *,
        params: CompetencyMatrixItemUpdateParams,
    ) -> CompetencyMatrixItem:
        item = await self._build_item_from_params(params=params)
        self._ensure_publishable(item=item)
        return await self.storage.update_competency_matrix_item(item=item)

    async def _build_item_from_params(
        self,
        *,
        params: CompetencyMatrixItemWriteParams,
    ) -> CompetencyMatrixItem:
        resource_ids_to_assign = params.get_resource_ids_to_assign()
        resources = (
            await self.storage.get_resources_by_ids(resource_ids=resource_ids_to_assign)
            if resource_ids_to_assign
            else ExternalResources(values=[])
        )
        if not resources.all_resources_exists_by_ids(ids=set(resource_ids_to_assign)):
            raise CompetencyMatrixItemNotFoundError
        return params.to_item(resources=resources, published_at=None)

    async def delete_item(self, *, item_id: IntId) -> None:
        await self.storage.delete_competency_matrix_item(item_id=item_id)

    async def switch_item_publish_status(
        self,
        *,
        params: CompetencyMatrixItemPublishStatusSwitchParams,
    ) -> None:
        if params.publish_status == PublishStatusEnum.PUBLISHED:
            item = await self.storage.get_competency_matrix_item(item_id=params.item_id)
            self._ensure_public_ready_fields(item=item)
        await self.storage.update_competency_matrix_item_publish_status(
            item_id=params.item_id,
            publish_status=params.publish_status,
        )

    def _ensure_publishable(self, *, item: CompetencyMatrixItem) -> None:
        if item.publish_status != PublishStatusEnum.PUBLISHED:
            return
        self._ensure_public_ready_fields(item=item)

    def _ensure_public_ready_fields(self, *, item: CompetencyMatrixItem) -> None:
        missing_fields = item.missing_publication_fields()
        if missing_fields:
            raise CompetencyMatrixItemNotPublicReadyError(missing_fields=missing_fields)

    async def suggest_question(
        self,
        *,
        params: QuestionSuggestionCreateParams,
    ) -> QueuedCompetencyMatrixQuestion:
        if params.limit is not None:
            await self.question_suggestion_limiter.check_create_allowed(params=params.limit)
        return await self.storage.create_queued_question(params=params.question)

    async def list_queued_questions(self) -> QueuedCompetencyMatrixQuestions:
        return await self.storage.list_queued_questions()

    async def import_queued_questions(
        self,
        *,
        params: QueuedCompetencyMatrixQuestionsCreateParams,
    ) -> QueuedCompetencyMatrixQuestions:
        return await self.storage.create_queued_questions(params=params)

    async def delete_queued_question(self, *, question_id: IntId) -> None:
        await self.storage.delete_queued_question(question_id=question_id)
