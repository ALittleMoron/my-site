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
    QueuedCompetencyMatrixQuestions,
    QueuedCompetencyMatrixQuestionsCreateParams,
)
from core.competency_matrix.services import QuestionSuggestionLimiter
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import CompetencyMatrixUseCase
from tests.test_cases import TestCase


class TestQuestionSuggestionsUseCase(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.storage.get_item_structure_by_subsection_id.return_value = (
            self.factory.core.competency_matrix_item_structure()
        )
        self.question_suggestion_limiter = Mock(spec=QuestionSuggestionLimiter)
        self.use_case = CompetencyMatrixUseCase(
            storage=self.storage,
            question_suggestion_limiter=self.question_suggestion_limiter,
        )

    async def test_suggest_question_delegates_limit_check_before_creating(self) -> None:
        now = datetime(2026, 6, 7, 12, 0, tzinfo=UTC)
        self.storage.create_queued_question.return_value = QueuedCompetencyMatrixQuestion(
            id=self.factory.core.hex_id(1),
            question="What is PEP 8?",
            grade=None,
            sheet=None,
            section=None,
            subsection=None,
            suggested_by_username=None,
            created_at=now,
        )

        params = QuestionSuggestionCreateParams(
            question=QueuedCompetencyMatrixQuestionCreateParams(
                question="What is PEP 8?",
                grade=None,
                sheet="python",
            ),
            limit=QuestionSuggestionLimitParams(
                client_identifier="203.0.113.10",
                now=now,
            ),
        )
        created_question = await self.use_case.suggest_question(params=params)

        assert created_question.question == "What is PEP 8?"
        self.question_suggestion_limiter.check_create_allowed.assert_called_once_with(
            params=params.limit,
        )
        self.storage.create_queued_question.assert_called_once_with(
            params=QueuedCompetencyMatrixQuestionCreateParams(
                question="What is PEP 8?",
                grade=None,
                sheet="python",
            ),
        )

    async def test_suggest_question_skips_quota_limiter_when_limit_is_absent(self) -> None:
        now = datetime(2026, 6, 7, 12, 0, tzinfo=UTC)
        queued_question = QueuedCompetencyMatrixQuestion(
            id=self.factory.core.hex_id(1),
            question="What is PEP 8?",
            grade=None,
            sheet=None,
            section=None,
            subsection=None,
            suggested_by_username=None,
            created_at=now,
        )
        params = QuestionSuggestionCreateParams(
            question=QueuedCompetencyMatrixQuestionCreateParams(
                question="What is PEP 8?",
                grade=None,
                sheet=None,
            ),
            limit=None,
        )
        self.storage.create_queued_question.return_value = queued_question

        created_question = await self.use_case.suggest_question(params=params)

        assert created_question == queued_question
        self.question_suggestion_limiter.check_create_allowed.assert_not_called()
        self.storage.create_queued_question.assert_called_once_with(params=params.question)

    async def test_import_queued_questions_creates_questions_without_quota_limiter(self) -> None:
        params = QueuedCompetencyMatrixQuestionsCreateParams(
            questions=[
                QueuedCompetencyMatrixQuestionCreateParams(
                    question="What is PEP 8?",
                    grade=None,
                    sheet="python",
                ),
                QueuedCompetencyMatrixQuestionCreateParams(
                    question="How does mypy help?",
                    grade=GradeEnum.MIDDLE,
                    sheet="python",
                ),
            ],
        )
        queued_questions = QueuedCompetencyMatrixQuestions(
            values=[
                self.factory.core.queued_competency_matrix_question(
                    question_id=1,
                    question="What is PEP 8?",
                    created_at=datetime(2026, 6, 7, 12, 0, tzinfo=UTC),
                ),
                self.factory.core.queued_competency_matrix_question(
                    question_id=2,
                    question="How does mypy help?",
                    created_at=datetime(2026, 6, 7, 12, 0, tzinfo=UTC),
                ),
            ],
        )
        self.storage.create_queued_questions.return_value = queued_questions

        created_questions = await self.use_case.import_queued_questions(params=params)

        assert created_questions == queued_questions
        self.question_suggestion_limiter.check_create_allowed.assert_not_called()
        self.storage.create_queued_questions.assert_called_once_with(params=params)

    async def test_create_item_from_queue_creates_item_then_removes_queue_entry(self) -> None:
        queued_question = QueuedCompetencyMatrixQuestion(
            id=self.factory.core.hex_id(7),
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
                queued_question_id=self.factory.core.hex_id(7),
                item=params,
            ),
        )

        assert item == created_item
        self.storage.get_queued_question.assert_called_once_with(
            question_id=self.factory.core.hex_id(7)
        )
        self.storage.create_competency_matrix_item.assert_called_once()
        self.storage.delete_queued_question.assert_called_once_with(
            question_id=self.factory.core.hex_id(7)
        )
        create_item_call_index = next(
            index
            for index, method_call in enumerate(self.storage.method_calls)
            if method_call[0] == "create_competency_matrix_item"
        )
        delete_queue_call_index = self.storage.method_calls.index(
            call.delete_queued_question(question_id=self.factory.core.hex_id(7)),
        )
        assert create_item_call_index < delete_queue_call_index

    async def test_create_item_from_queue_does_not_delete_missing_queue_entry(self) -> None:
        self.storage.get_queued_question.side_effect = QueuedCompetencyMatrixQuestionNotFoundError

        with pytest.raises(QueuedCompetencyMatrixQuestionNotFoundError):
            await self.use_case.create_item_from_queue(
                params=QueuedCompetencyMatrixQuestionCreateItemParams(
                    queued_question_id=self.factory.core.hex_id(404),
                    item=self.factory.core.competency_matrix_item_create_params(item_id=1),
                ),
            )

        self.storage.create_competency_matrix_item.assert_not_called()
        self.storage.delete_queued_question.assert_not_called()
