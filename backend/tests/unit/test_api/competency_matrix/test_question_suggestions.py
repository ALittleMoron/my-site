from datetime import UTC, datetime
from io import BytesIO
from typing import cast
from unittest.mock import ANY, Mock

import pytest_asyncio
from httpx import codes
from litestar import Request
from litestar.datastructures import State
from openpyxl import Workbook

from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.exceptions import (
    QuestionSuggestionQuotaExceededError,
    QueuedCompetencyMatrixQuestionNotFoundError,
)
from core.competency_matrix.schemas import (
    QuestionSuggestionCreateParams,
    QueuedCompetencyMatrixQuestionCreateItemParams,
    QueuedCompetencyMatrixQuestionCreateParams,
    QueuedCompetencyMatrixQuestions,
)
from core.enums import PublishStatusEnum
from core.types import IntId
from entrypoints.litestar.api.competency_matrix.dependencies import (
    provide_question_suggestion_limit_params,
)
from entrypoints.litestar.api.competency_matrix.endpoints import PublicCompetencyMatrixApiController
from tests.test_cases import ApiTestCase


class TestQuestionSuggestionsApi(ApiTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.authentication_use_case = await self.container.get_auth_use_case()
        self.use_case = await self.container.get_competency_matrix_use_case()

    def test_anonymous_user_can_suggest_question(self) -> None:
        response = self.no_auth_api.post_question_suggestion(
            question="  What is PEP 8?  ",
            sheet="python",
        )

        self.asserts.status(response=response, expected_status=codes.NO_CONTENT)
        self.use_case.suggest_question.assert_called_once_with(
            params=ANY,
        )
        call_params = self.use_case.suggest_question.call_args.kwargs["params"]
        assert isinstance(call_params, QuestionSuggestionCreateParams)
        assert call_params.question == QueuedCompetencyMatrixQuestionCreateParams(
            question="What is PEP 8?",
            sheet="python",
            grade=None,
        )
        assert call_params.limit is not None
        assert call_params.limit.client_identifier != ""
        assert call_params.limit.now.tzinfo is not None

    def test_anonymous_user_can_suggest_question_without_sheet_key(self) -> None:
        response = self.no_auth_api.client.post(
            "/api/competency-matrix/question-suggestions",
            json={"question": "What is PEP 8?"},
        )

        self.asserts.status(response=response, expected_status=codes.NO_CONTENT)
        call_params = self.use_case.suggest_question.call_args.kwargs["params"]
        assert call_params.question == QueuedCompetencyMatrixQuestionCreateParams(
            question="What is PEP 8?",
            sheet=None,
            grade=None,
        )

    def test_anonymous_suggestion_uses_forwarded_client_identifier(self) -> None:
        response = self.no_auth_api.post_question_suggestion(
            question="What is PEP 8?",
            headers={"X-Forwarded-For": "203.0.113.10, 10.0.0.2"},
        )

        self.asserts.status(response=response, expected_status=codes.NO_CONTENT)
        self.use_case.suggest_question.assert_called_once_with(
            params=ANY,
        )
        call_params = self.use_case.suggest_question.call_args.kwargs["params"]
        assert call_params == QuestionSuggestionCreateParams(
            question=QueuedCompetencyMatrixQuestionCreateParams(
                question="What is PEP 8?",
                sheet=None,
                grade=None,
            ),
            limit=call_params.limit,
        )
        assert call_params.limit is not None
        assert call_params.limit.client_identifier == "203.0.113.10"
        assert call_params.limit.now.tzinfo is not None

    def test_question_suggestion_limit_dependency_uses_forwarded_client_identifier(self) -> None:
        request = cast(
            "Request[JwtUser, Token | None, State]",
            Mock(
                headers={"x-forwarded-for": "203.0.113.10, 10.0.0.2"},
                client=Mock(host="198.51.100.4"),
            ),
        )

        params = provide_question_suggestion_limit_params(request=request)

        assert params.client_identifier == "203.0.113.10"
        assert params.now.tzinfo is not None

    def test_competency_matrix_controller_does_not_keep_client_identifier_helper(self) -> None:
        assert "_client_identifier" not in PublicCompetencyMatrixApiController.__dict__

    def test_suggest_question_rejects_empty_question(self) -> None:
        response = self.no_auth_api.post_question_suggestion(question="")

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.suggest_question.assert_not_called()

    def test_suggest_question_rejects_blank_question(self) -> None:
        response = self.no_auth_api.post_question_suggestion(question="   ")

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.suggest_question.assert_not_called()

    def test_suggest_question_returns_429_when_daily_quota_is_exhausted(self) -> None:
        self.use_case.suggest_question.side_effect = QuestionSuggestionQuotaExceededError

        response = self.no_auth_api.post_question_suggestion(question="What is PEP 8?")

        self.asserts.error_message(
            response=response,
            expected_status=codes.TOO_MANY_REQUESTS,
            expected_message="Question suggestion daily quota exceeded",
        )

    def test_content_manager_can_list_queue_in_fifo_order(self) -> None:
        self.use_case.list_queued_questions.return_value = QueuedCompetencyMatrixQuestions(
            values=[
                self.factory.core.queued_competency_matrix_question(
                    question_id=1,
                    question="First question",
                    created_at=datetime(2026, 6, 7, 12, 0, tzinfo=UTC),
                ),
                self.factory.core.queued_competency_matrix_question(
                    question_id=2,
                    question="Second question",
                    grade=GradeEnum.JUNIOR,
                    sheet="Python",
                    section="Core",
                    subsection="Syntax",
                    suggested_by_username="alice",
                    created_at=datetime(2026, 6, 7, 12, 1, tzinfo=UTC),
                ),
            ],
        )

        response = self.api.get_queued_matrix_questions()

        self.asserts.json_body(
            response=response,
            expected_status=codes.OK,
            expected_body={
                "questions": [
                    {
                        "id": 1,
                        "question": "First question",
                        "grade": None,
                        "sheet": None,
                        "section": None,
                        "subsection": None,
                        "suggestedByUsername": None,
                        "createdAt": "2026-06-07T12:00:00+00:00",
                    },
                    {
                        "id": 2,
                        "question": "Second question",
                        "grade": "Junior",
                        "sheet": "Python",
                        "section": "Core",
                        "subsection": "Syntax",
                        "suggestedByUsername": "alice",
                        "createdAt": "2026-06-07T12:01:00+00:00",
                    },
                ],
            },
        )
        self.use_case.list_queued_questions.assert_called_once_with()

    def test_regular_user_cannot_list_queue(self) -> None:
        self.authentication_use_case.authenticate.return_value = JwtUser(
            username="user",
            role=RoleEnum.USER,
        )

        response = self.api.get_queued_matrix_questions()

        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)
        self.use_case.list_queued_questions.assert_not_called()

    def test_content_manager_can_create_queued_question(self) -> None:
        self.use_case.suggest_question.return_value = (
            self.factory.core.queued_competency_matrix_question(
                question_id=3,
                question="What is PEP 8?",
                created_at=datetime(2026, 6, 7, 12, 3, tzinfo=UTC),
            )
        )

        response = self.api.post_create_queued_matrix_question(question="  What is PEP 8?  ")

        self.asserts.json_body(
            response=response,
            expected_status=codes.CREATED,
            expected_body={
                "id": 3,
                "question": "What is PEP 8?",
                "grade": None,
                "sheet": None,
                "section": None,
                "subsection": None,
                "suggestedByUsername": None,
                "createdAt": "2026-06-07T12:03:00+00:00",
            },
        )
        self.use_case.suggest_question.assert_called_once_with(params=ANY)
        call_params = self.use_case.suggest_question.call_args.kwargs["params"]
        assert call_params == QuestionSuggestionCreateParams(
            question=QueuedCompetencyMatrixQuestionCreateParams(
                question="What is PEP 8?",
                sheet=None,
                grade=None,
            ),
            limit=None,
        )

    def test_content_manager_can_import_txt_queued_questions(self) -> None:
        self.use_case.import_queued_questions.return_value = QueuedCompetencyMatrixQuestions(
            values=[
                self.factory.core.queued_competency_matrix_question(
                    question_id=3,
                    question="What is PEP 8?",
                    created_at=datetime(2026, 6, 7, 12, 3, tzinfo=UTC),
                ),
                self.factory.core.queued_competency_matrix_question(
                    question_id=4,
                    question="How does mypy help?",
                    created_at=datetime(2026, 6, 7, 12, 3, tzinfo=UTC),
                ),
            ],
        )

        response = self.api.post_import_queued_matrix_questions(
            filename="questions.txt",
            content=b"What is PEP 8?\nHow does mypy help?",
            content_type="text/plain",
        )

        self.asserts.status(response=response, expected_status=codes.CREATED)
        body = response.json()
        assert body["questions"] == [
            {
                "id": 3,
                "question": "What is PEP 8?",
                "grade": None,
                "sheet": None,
                "section": None,
                "subsection": None,
                "suggestedByUsername": None,
                "createdAt": "2026-06-07T12:03:00+00:00",
            },
            {
                "id": 4,
                "question": "How does mypy help?",
                "grade": None,
                "sheet": None,
                "section": None,
                "subsection": None,
                "suggestedByUsername": None,
                "createdAt": "2026-06-07T12:03:00+00:00",
            },
        ]
        self.use_case.import_queued_questions.assert_called_once_with(params=ANY)
        call_params = self.use_case.import_queued_questions.call_args.kwargs["params"]
        assert self.collections.pluck(items=call_params.questions, attr="question") == [
            "What is PEP 8?",
            "How does mypy help?",
        ]

    def test_content_manager_can_import_csv_queued_questions(self) -> None:
        self.use_case.import_queued_questions.return_value = QueuedCompetencyMatrixQuestions(
            values=[
                self.factory.core.queued_competency_matrix_question(
                    question_id=5,
                    question="What is PEP 8?",
                    grade=GradeEnum.JUNIOR,
                    sheet="python",
                    created_at=datetime(2026, 6, 7, 12, 5, tzinfo=UTC),
                ),
            ],
        )

        response = self.api.post_import_queued_matrix_questions(
            filename="questions.csv",
            content="question;sheet;grade\nЧто такое PEP 8?;python;Junior".encode(),
            content_type="text/csv",
        )

        self.asserts.status(response=response, expected_status=codes.CREATED)
        self.use_case.import_queued_questions.assert_called_once_with(params=ANY)
        call_params = self.use_case.import_queued_questions.call_args.kwargs["params"]
        assert self.collections.pluck(items=call_params.questions, attr="question") == [
            "Что такое PEP 8?",
        ]
        assert self.collections.pluck(items=call_params.questions, attr="sheet") == ["python"]
        assert self.collections.pluck(items=call_params.questions, attr="grade") == [
            GradeEnum.JUNIOR,
        ]

    def test_import_normalizes_line_breaks_inside_question_text(self) -> None:
        self.use_case.import_queued_questions.return_value = QueuedCompetencyMatrixQuestions(
            values=[
                self.factory.core.queued_competency_matrix_question(
                    question_id=8,
                    question="What is PEP 8?",
                    created_at=datetime(2026, 6, 7, 12, 8, tzinfo=UTC),
                ),
            ],
        )

        response = self.api.post_import_queued_matrix_questions(
            filename="questions.csv",
            content=b'question\n"What is PEP 8?\nHow should it be used?"',
            content_type="text/csv",
        )

        self.asserts.status(response=response, expected_status=codes.CREATED)
        self.use_case.import_queued_questions.assert_called_once_with(params=ANY)
        call_params = self.use_case.import_queued_questions.call_args.kwargs["params"]
        assert self.collections.pluck(items=call_params.questions, attr="question") == [
            "What is PEP 8? How should it be used?",
        ]

    def test_content_manager_can_import_xlsx_queued_questions(self) -> None:
        self.use_case.import_queued_questions.return_value = QueuedCompetencyMatrixQuestions(
            values=[
                self.factory.core.queued_competency_matrix_question(
                    question_id=6,
                    question="What is PEP 8?",
                    created_at=datetime(2026, 6, 7, 12, 6, tzinfo=UTC),
                ),
            ],
        )

        response = self.api.post_import_queued_matrix_questions(
            filename="questions.xlsx",
            content=xlsx_bytes([["questions"], ["What is PEP 8?"]]),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        self.asserts.status(response=response, expected_status=codes.CREATED)
        self.use_case.import_queued_questions.assert_called_once_with(params=ANY)
        call_params = self.use_case.import_queued_questions.call_args.kwargs["params"]
        assert self.collections.pluck(items=call_params.questions, attr="question") == [
            "What is PEP 8?",
        ]

    def test_content_manager_can_import_xlsm_queued_questions_without_header(self) -> None:
        self.use_case.import_queued_questions.return_value = QueuedCompetencyMatrixQuestions(
            values=[
                self.factory.core.queued_competency_matrix_question(
                    question_id=7,
                    question="What is PEP 8?",
                    created_at=datetime(2026, 6, 7, 12, 7, tzinfo=UTC),
                ),
            ],
        )

        response = self.api.post_import_queued_matrix_questions(
            filename="questions.xlsm",
            content=xlsx_bytes([["What is PEP 8?"]]),
            content_type="application/vnd.ms-excel.sheet.macroEnabled.12",
        )

        self.asserts.status(response=response, expected_status=codes.CREATED)
        self.use_case.import_queued_questions.assert_called_once_with(params=ANY)
        call_params = self.use_case.import_queued_questions.call_args.kwargs["params"]
        assert self.collections.pluck(items=call_params.questions, attr="question") == [
            "What is PEP 8?",
        ]

    def test_regular_user_cannot_import_queued_questions(self) -> None:
        self.authentication_use_case.authenticate.return_value = JwtUser(
            username="user",
            role=RoleEnum.USER,
        )

        response = self.api.post_import_queued_matrix_questions(
            filename="questions.txt",
            content=b"What is PEP 8?",
            content_type="text/plain",
        )

        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)
        self.use_case.import_queued_questions.assert_not_called()

    def test_import_rejects_csv_without_question_header(self) -> None:
        response = self.api.post_import_queued_matrix_questions(
            filename="questions.csv",
            content=b"title\nWhat is PEP 8?",
            content_type="text/csv",
        )

        body = self.asserts.error_message(
            response=response,
            expected_status=codes.BAD_REQUEST,
            expected_message="Question queue import file is invalid.",
        )
        assert body["nested_errors"][0]["message"] == (
            "CSV header must contain one of: question, questions, вопрос, вопросы."
        )
        self.use_case.import_queued_questions.assert_not_called()

    def test_import_rejects_legacy_xls_file(self) -> None:
        response = self.api.post_import_queued_matrix_questions(
            filename="questions.xls",
            content=b"not an xls file",
            content_type="application/vnd.ms-excel",
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        body = response.json()
        assert body["nested_errors"][0]["message"] == ("Unsupported import file extension: .xls.")
        self.use_case.import_queued_questions.assert_not_called()

    def test_import_rejects_empty_txt_lines_without_creating_questions(self) -> None:
        response = self.api.post_import_queued_matrix_questions(
            filename="questions.txt",
            content=b"What is PEP 8?\n\nHow does mypy help?",
            content_type="text/plain",
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        body = response.json()
        assert body["nested_errors"][0]["message"] == "Row 2 question must not be blank."
        self.use_case.import_queued_questions.assert_not_called()

    def test_import_rejects_long_questions_without_creating_questions(self) -> None:
        response = self.api.post_import_queued_matrix_questions(
            filename="questions.txt",
            content=("x" * 256).encode(),
            content_type="text/plain",
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        body = response.json()
        assert body["nested_errors"][0]["message"] == (
            "Row 1 question must be at most 255 characters."
        )
        self.use_case.import_queued_questions.assert_not_called()

    def test_import_rejects_non_text_excel_cells_without_creating_questions(self) -> None:
        response = self.api.post_import_queued_matrix_questions(
            filename="questions.xlsx",
            content=xlsx_bytes([["questions"], [42]]),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        body = response.json()
        assert body["nested_errors"][0]["message"] == "Row 2 question must be text."
        self.use_case.import_queued_questions.assert_not_called()

    def test_regular_user_cannot_create_queued_question(self) -> None:
        self.authentication_use_case.authenticate.return_value = JwtUser(
            username="user",
            role=RoleEnum.USER,
        )

        response = self.api.post_create_queued_matrix_question(question="What is PEP 8?")

        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)
        self.use_case.suggest_question.assert_not_called()

    def test_create_queued_question_rejects_blank_question(self) -> None:
        response = self.api.post_create_queued_matrix_question(question="   ")

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.suggest_question.assert_not_called()

    def test_content_manager_can_reject_queue_entry(self) -> None:
        response = self.api.delete_queued_matrix_question(question_id=7)

        self.asserts.status(response=response, expected_status=codes.NO_CONTENT)
        self.use_case.delete_queued_question.assert_called_once_with(question_id=IntId(7))

    def test_reject_queue_entry_returns_not_found(self) -> None:
        self.use_case.delete_queued_question.side_effect = (
            QueuedCompetencyMatrixQuestionNotFoundError
        )

        response = self.api.delete_queued_matrix_question(question_id=404)

        self.asserts.error_message(
            response=response,
            expected_status=codes.NOT_FOUND,
            expected_message="Queued competency matrix question not found",
        )

    def test_content_manager_can_create_matrix_item_from_queue_entry(self) -> None:
        self.use_case.create_item_from_queue.return_value = (
            self.factory.core.competency_matrix_item(
                item_id=10,
                question_ru="Что такое PEP 8?",
                question_en="What is PEP 8?",
                answer_ru="Ответ",
                answer_en="Answer",
                interview_expected_answer_ru="Ожидаемый ответ",
                interview_expected_answer_en="Expected answer",
                sheet_key="python",
                sheet_ru="Питон",
                sheet_en="Python",
                grade=GradeEnum.JUNIOR,
                section_ru="Основы",
                section_en="Core",
                subsection_ru="Стиль",
                subsection_en="Style",
                publish_status=PublishStatusEnum.DRAFT,
            )
        )

        response = self.api.post_create_item_from_queue(
            question_id=7,
            data=self.factory.api.competency_matrix_item_request(
                question_ru="Что такое PEP 8?",
                question_en="What is PEP 8?",
                answer_ru="Ответ",
                answer_en="Answer",
                interview_expected_answer_ru="Ожидаемый ответ",
                interview_expected_answer_en="Expected answer",
                sheet_key="python",
                sheet_ru="Питон",
                sheet_en="Python",
                grade="Junior",
                section_ru="Основы",
                section_en="Core",
                subsection_ru="Стиль",
                subsection_en="Style",
                resources=[],
            ),
            language="en",
        )

        self.asserts.status(response=response, expected_status=codes.CREATED)
        body = response.json()
        assert body["id"] == "10"
        assert body["question"] == "What is PEP 8?"
        self.use_case.create_item_from_queue.assert_called_once_with(
            params=ANY,
        )
        call_params = self.use_case.create_item_from_queue.call_args.kwargs["params"]
        assert isinstance(call_params, QueuedCompetencyMatrixQuestionCreateItemParams)
        assert call_params.queued_question_id == IntId(7)


def xlsx_bytes(rows: list[list[object]]) -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    for row in rows:
        worksheet.append(row)
    stream = BytesIO()
    workbook.save(stream)
    return stream.getvalue()
