from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.exceptions import QueuedCompetencyMatrixQuestionNotFoundError
from core.competency_matrix.schemas import (
    QueuedCompetencyMatrixQuestion,
    QueuedCompetencyMatrixQuestionCreateParams,
    QueuedCompetencyMatrixQuestionsCreateParams,
)
from infra.postgresql.storages.competency_matrix import CompetencyMatrixDatabaseStorage
from tests.test_cases import StorageTestCase


class TestCompetencyMatrixQuestionQueueStorage(StorageTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, session: AsyncSession) -> None:
        self.storage = CompetencyMatrixDatabaseStorage(session=session)

    async def test_create_and_list_queued_questions_in_fifo_order(self) -> None:
        first_created_at = datetime(2026, 6, 7, 12, 0, tzinfo=UTC)
        second_created_at = datetime(2026, 6, 7, 12, 1, tzinfo=UTC)
        third_created_at = datetime(2026, 6, 7, 12, 2, tzinfo=UTC)
        await self.storage_helper.create_queued_matrix_questions(
            questions=[
                QueuedCompetencyMatrixQuestion(
                    id=self.factory.core.hex_id(2),
                    question="Earliest",
                    grade=GradeEnum.JUNIOR,
                    sheet="Python",
                    section="Core",
                    subsection="Syntax",
                    suggested_by_username=None,
                    created_at=first_created_at,
                ),
                QueuedCompetencyMatrixQuestion(
                    id=self.factory.core.hex_id(1),
                    question="Middle",
                    grade=None,
                    sheet=None,
                    section=None,
                    subsection=None,
                    suggested_by_username=None,
                    created_at=second_created_at,
                ),
                QueuedCompetencyMatrixQuestion(
                    id=self.factory.core.hex_id(3),
                    question="Latest",
                    grade=None,
                    sheet=None,
                    section=None,
                    subsection=None,
                    suggested_by_username=None,
                    created_at=third_created_at,
                ),
            ],
        )

        questions = await self.storage.list_queued_questions()

        assert [question.id for question in questions] == [
            self.factory.core.hex_id(2),
            self.factory.core.hex_id(1),
            self.factory.core.hex_id(3),
        ]

    async def test_create_queued_question_returns_persisted_question(self) -> None:
        question = await self.storage.create_queued_question(
            params=QueuedCompetencyMatrixQuestionCreateParams(
                question="What is PEP 8?",
                sheet="python",
                grade=GradeEnum.JUNIOR,
            ),
        )

        self.asserts.hex_id(question.id)
        assert question.question == "What is PEP 8?"
        assert question.grade == GradeEnum.JUNIOR
        assert question.sheet == "python"
        assert question.section is None
        assert question.subsection is None
        assert question.suggested_by_username is None

    async def test_create_queued_questions_returns_persisted_questions_in_input_order(self) -> None:
        questions = await self.storage.create_queued_questions(
            params=QueuedCompetencyMatrixQuestionsCreateParams(
                questions=[
                    QueuedCompetencyMatrixQuestionCreateParams(
                        question="What is PEP 8?",
                        sheet="python",
                        grade=None,
                    ),
                    QueuedCompetencyMatrixQuestionCreateParams(
                        question="How does mypy help?",
                        sheet="python",
                        grade=GradeEnum.MIDDLE,
                    ),
                ],
            ),
        )

        assert [question.question for question in questions] == [
            "What is PEP 8?",
            "How does mypy help?",
        ]
        assert [question.sheet for question in questions] == ["python", "python"]
        assert [question.grade for question in questions] == [None, GradeEnum.MIDDLE]
        assert [question.section for question in questions] == [None, None]
        assert [question.subsection for question in questions] == [None, None]
        self.asserts.hex_id(questions.values[0].id)
        self.asserts.hex_id(questions.values[1].id)
        assert questions.values[0].id != questions.values[1].id
        assert questions.values[0].created_at == questions.values[1].created_at

    async def test_list_queued_questions_breaks_fifo_ties_by_id(self) -> None:
        created_at = datetime(2026, 6, 7, 12, 0, tzinfo=UTC)
        await self.storage_helper.create_queued_matrix_questions(
            questions=[
                QueuedCompetencyMatrixQuestion(
                    id=self.factory.core.hex_id(2),
                    question="Second",
                    grade=None,
                    sheet=None,
                    section=None,
                    subsection=None,
                    suggested_by_username=None,
                    created_at=created_at,
                ),
                QueuedCompetencyMatrixQuestion(
                    id=self.factory.core.hex_id(1),
                    question="First",
                    grade=None,
                    sheet=None,
                    section=None,
                    subsection=None,
                    suggested_by_username=None,
                    created_at=created_at,
                ),
            ],
        )

        questions = await self.storage.list_queued_questions()

        assert [question.id for question in questions] == [
            self.factory.core.hex_id(1),
            self.factory.core.hex_id(2),
        ]

    async def test_get_queued_question_not_found(self) -> None:
        with pytest.raises(QueuedCompetencyMatrixQuestionNotFoundError):
            await self.storage.get_queued_question(question_id=self.factory.core.hex_id(404))

    async def test_delete_queued_question_removes_pending_entry(self) -> None:
        await self.storage_helper.create_queued_matrix_questions(
            questions=[
                QueuedCompetencyMatrixQuestion(
                    id=self.factory.core.hex_id(7),
                    question="What is PEP 8?",
                    grade=None,
                    sheet=None,
                    section=None,
                    subsection=None,
                    suggested_by_username=None,
                    created_at=datetime(2026, 6, 7, 12, 0, tzinfo=UTC),
                ),
            ],
        )

        await self.storage.delete_queued_question(question_id=self.factory.core.hex_id(7))

        questions = await self.storage.list_queued_questions()
        assert questions.values == []
