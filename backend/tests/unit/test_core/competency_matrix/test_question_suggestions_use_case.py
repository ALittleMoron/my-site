from datetime import UTC, datetime
from unittest.mock import Mock, call

import pytest

from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.exceptions import (
    QueuedCompetencyMatrixQuestionNotFoundError,
)
from core.competency_matrix.schemas import (
    QuestionSuggestionCreateParams,
    QuestionSuggestionLimitParams,
    QueuedCompetencyMatrixQuestion,
    QueuedCompetencyMatrixQuestionCreateItemParams,
    QueuedCompetencyMatrixQuestionCreateParams,
)
from core.competency_matrix.services import QuestionSuggestionLimiter
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import CompetencyMatrixUseCase
from core.types import IntId
from tests.unit.fixtures import FactoryFixture


class TestQuestionSuggestionsUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.question_suggestion_limiter = Mock(spec=QuestionSuggestionLimiter)
        self.use_case = CompetencyMatrixUseCase(
            storage=self.storage,
            question_suggestion_limiter=self.question_suggestion_limiter,
        )

    async def test_suggest_question_delegates_limit_check_before_creating(self) -> None:
        now = datetime(2026, 6, 7, 12, 0, tzinfo=UTC)
        self.storage.create_queued_question.return_value = QueuedCompetencyMatrixQuestion(
            id=IntId(1),
            question="What is PEP 8?",
            grade=None,
            sheet=None,
            section=None,
            subsection=None,
            suggested_by_username=None,
            created_at=now,
        )

        params = QuestionSuggestionCreateParams(
            question=QueuedCompetencyMatrixQuestionCreateParams(question="What is PEP 8?"),
            limit=QuestionSuggestionLimitParams(
                client_identifier="203.0.113.10",
                now=now,
            ),
        )
        await self.use_case.suggest_question(params=params)

        self.question_suggestion_limiter.check_create_allowed.assert_called_once_with(
            params=params.limit,
        )
        self.storage.create_queued_question.assert_called_once_with(
            params=QueuedCompetencyMatrixQuestionCreateParams(question="What is PEP 8?"),
        )

    async def test_create_item_from_queue_creates_item_then_removes_queue_entry(self) -> None:
        queued_question = QueuedCompetencyMatrixQuestion(
            id=IntId(7),
            question="What is PEP 8?",
            grade=GradeEnum.JUNIOR,
            sheet="Python",
            section="Core",
            subsection="Style",
            suggested_by_username=None,
            created_at=datetime(2026, 6, 7, 12, 0, tzinfo=UTC),
        )
        params = self.factory.core.competency_matrix_item_create_params(
            item_id=10,
            question_ru="Что такое PEP 8?",
            question_en="What is PEP 8?",
            grade=GradeEnum.JUNIOR,
            sheet="Python",
            section="Core",
            subsection="Style",
        )
        created_item = self.factory.core.competency_matrix_item(
            item_id=10,
            question_en="What is PEP 8?",
        )
        self.storage.get_queued_question.return_value = queued_question
        self.storage.create_competency_matrix_item.return_value = created_item

        item = await self.use_case.create_item_from_queue(
            params=QueuedCompetencyMatrixQuestionCreateItemParams(
                queued_question_id=IntId(7),
                item=params,
            ),
        )

        assert item == created_item
        self.storage.get_queued_question.assert_called_once_with(question_id=IntId(7))
        self.storage.create_competency_matrix_item.assert_called_once()
        self.storage.delete_queued_question.assert_called_once_with(question_id=IntId(7))
        create_item_call_index = next(
            index
            for index, method_call in enumerate(self.storage.method_calls)
            if method_call[0] == "create_competency_matrix_item"
        )
        delete_queue_call_index = self.storage.method_calls.index(
            call.delete_queued_question(question_id=IntId(7)),
        )
        assert create_item_call_index < delete_queue_call_index

    async def test_create_item_from_queue_does_not_delete_missing_queue_entry(self) -> None:
        self.storage.get_queued_question.side_effect = QueuedCompetencyMatrixQuestionNotFoundError

        with pytest.raises(QueuedCompetencyMatrixQuestionNotFoundError):
            await self.use_case.create_item_from_queue(
                params=QueuedCompetencyMatrixQuestionCreateItemParams(
                    queued_question_id=IntId(404),
                    item=self.factory.core.competency_matrix_item_create_params(item_id=1),
                ),
            )

        self.storage.create_competency_matrix_item.assert_not_called()
        self.storage.delete_queued_question.assert_not_called()
