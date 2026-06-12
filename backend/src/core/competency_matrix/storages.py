from abc import ABC, abstractmethod

from core.competency_matrix.schemas import (
    CompetencyMatrixFilterOptions,
    CompetencyMatrixItem,
    CompetencyMatrixItemFilters,
    CompetencyMatrixWorkspaceFilters,
    CompetencyMatrixWorkspaceItem,
    CompetencyMatrixWorkspaceSummary,
    ExternalResources,
    QuestionSuggestionQuota,
    QueuedCompetencyMatrixQuestion,
    QueuedCompetencyMatrixQuestionCreateParams,
    QueuedCompetencyMatrixQuestions,
    QueuedCompetencyMatrixQuestionsCreateParams,
    Sheets,
)
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import IntId


class CompetencyMatrixStorage(ABC):
    @abstractmethod
    async def list_sheets(self) -> Sheets:
        raise NotImplementedError

    @abstractmethod
    async def list_competency_matrix_items(
        self,
        *,
        filters: CompetencyMatrixItemFilters,
    ) -> list[CompetencyMatrixItem]:
        raise NotImplementedError

    @abstractmethod
    async def list_competency_matrix_workspace_items(
        self,
        *,
        filters: CompetencyMatrixWorkspaceFilters,
    ) -> tuple[
        list[CompetencyMatrixWorkspaceItem],
        int,
        CompetencyMatrixWorkspaceSummary,
    ]:
        raise NotImplementedError

    @abstractmethod
    async def list_competency_matrix_workspace_filter_options(
        self,
        *,
        language: LanguageEnum,
    ) -> CompetencyMatrixFilterOptions:
        raise NotImplementedError

    @abstractmethod
    async def get_competency_matrix_item(self, item_id: IntId) -> CompetencyMatrixItem:
        raise NotImplementedError

    @abstractmethod
    async def get_competency_matrix_item_by_slug(self, slug: str) -> CompetencyMatrixItem:
        raise NotImplementedError

    @abstractmethod
    async def create_competency_matrix_item(
        self,
        item: CompetencyMatrixItem,
    ) -> CompetencyMatrixItem:
        raise NotImplementedError

    @abstractmethod
    async def update_competency_matrix_item(
        self,
        item: CompetencyMatrixItem,
    ) -> CompetencyMatrixItem:
        raise NotImplementedError

    @abstractmethod
    async def update_competency_matrix_item_publish_status(
        self,
        item_id: IntId,
        publish_status: PublishStatusEnum,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_resources_by_ids(
        self,
        resource_ids: list[IntId],
    ) -> ExternalResources:
        raise NotImplementedError

    @abstractmethod
    async def delete_competency_matrix_item(self, item_id: IntId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def search_competency_matrix_resources(
        self,
        search_name: str,
        limit: int,
        language: LanguageEnum,
    ) -> ExternalResources:
        raise NotImplementedError

    @abstractmethod
    async def list_queued_questions(self) -> QueuedCompetencyMatrixQuestions:
        raise NotImplementedError

    @abstractmethod
    async def get_queued_question(self, question_id: IntId) -> QueuedCompetencyMatrixQuestion:
        raise NotImplementedError

    @abstractmethod
    async def create_queued_question(
        self,
        *,
        params: QueuedCompetencyMatrixQuestionCreateParams,
    ) -> QueuedCompetencyMatrixQuestion:
        raise NotImplementedError

    @abstractmethod
    async def create_queued_questions(
        self,
        *,
        params: QueuedCompetencyMatrixQuestionsCreateParams,
    ) -> QueuedCompetencyMatrixQuestions:
        raise NotImplementedError

    @abstractmethod
    async def delete_queued_question(self, question_id: IntId) -> None:
        raise NotImplementedError


class QuestionSuggestionQuotaStorage(ABC):
    @abstractmethod
    async def consume_question_suggestion_quota(
        self,
        *,
        actor_key: str,
        limit: int,
        ttl_seconds: int,
    ) -> QuestionSuggestionQuota:
        raise NotImplementedError
