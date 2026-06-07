from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.exceptions import QueuedCompetencyMatrixQuestionNotFoundError
from core.competency_matrix.schemas import (
    QueuedCompetencyMatrixQuestion,
    QueuedCompetencyMatrixQuestionCreateParams,
)
from core.types import IntId
from infra.postgresql.storages.competency_matrix import CompetencyMatrixDatabaseStorage
from tests.fixtures import StorageFixture


class TestCompetencyMatrixQuestionQueueStorage(StorageFixture):
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
                    id=IntId(2),
                    question="Earliest",
                    grade=GradeEnum.JUNIOR,
                    sheet="Python",
                    section="Core",
                    subsection="Syntax",
                    suggested_by_username=None,
                    created_at=first_created_at,
                ),
                QueuedCompetencyMatrixQuestion(
                    id=IntId(1),
                    question="Middle",
                    grade=None,
                    sheet=None,
                    section=None,
                    subsection=None,
                    suggested_by_username=None,
                    created_at=second_created_at,
                ),
                QueuedCompetencyMatrixQuestion(
                    id=IntId(3),
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

        assert [question.id for question in questions] == [2, 1, 3]

    async def test_create_queued_question_returns_persisted_question(self) -> None:
        question = await self.storage.create_queued_question(
            params=QueuedCompetencyMatrixQuestionCreateParams(question="What is PEP 8?"),
        )

        assert question.id > 0
        assert question.question == "What is PEP 8?"
        assert question.grade is None
        assert question.suggested_by_username is None

    async def test_get_queued_question_not_found(self) -> None:
        with pytest.raises(QueuedCompetencyMatrixQuestionNotFoundError):
            await self.storage.get_queued_question(question_id=IntId(404))

    async def test_delete_queued_question_removes_pending_entry(self) -> None:
        await self.storage_helper.create_queued_matrix_questions(
            questions=[
                QueuedCompetencyMatrixQuestion(
                    id=IntId(7),
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

        await self.storage.delete_queued_question(question_id=IntId(7))

        questions = await self.storage.list_queued_questions()
        assert questions.values == []
