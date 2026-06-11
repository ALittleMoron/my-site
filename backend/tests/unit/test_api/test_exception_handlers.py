from collections.abc import Sequence

from httpx import Response, codes
from litestar import Litestar, get
from litestar.testing import TestClient
from litestar.types import ControllerRouterHandler
from verbose_http_exceptions import (
    BadRequestHTTPException,
    ForbiddenHTTPException,
    InternalServerErrorHTTPException,
    NotFoundHTTPException,
    TooManyRequestsHTTPException,
    UnauthorizedHTTPException,
)

from core.auth.exceptions import ForbiddenError, UnauthorizedError
from core.competency_matrix.exceptions import (
    QuestionQueueImportInvalidError,
    QuestionQueueImportIssue,
    QuestionSuggestionQuotaExceededError,
)
from core.exceptions import DomainError, EntryNotFoundError
from core.files.exceptions import FileStorageInternalError, InvalidFileDataError
from entrypoints.litestar import exception_handlers
from entrypoints.litestar.exception_handlers import get_litestar_exception_handlers


@get("/entry-not-found", sync_to_thread=False)
def raise_entry_not_found() -> None:
    raise EntryNotFoundError


@get("/unauthorized", sync_to_thread=False)
def raise_unauthorized() -> None:
    raise UnauthorizedError


@get("/forbidden", sync_to_thread=False)
def raise_forbidden() -> None:
    raise ForbiddenError


@get("/question-quota", sync_to_thread=False)
def raise_question_quota() -> None:
    raise QuestionSuggestionQuotaExceededError


@get("/question-import", sync_to_thread=False)
def raise_question_import() -> None:
    raise QuestionQueueImportInvalidError(
        issues=[
            QuestionQueueImportIssue(
                message="Row 2 question must not be blank.",
                row_number=2,
            ),
        ],
    )


@get("/python-error", sync_to_thread=False)
def raise_python_error() -> None:
    msg = "plain python error"
    raise ValueError(msg)


def test_not_found_domain_error_returns_verbose_404() -> None:
    response = get_response("/entry-not-found")

    assert response.status_code == codes.NOT_FOUND
    assert response.json()["message"] == EntryNotFoundError.message


def test_unauthorized_domain_error_returns_verbose_401() -> None:
    response = get_response("/unauthorized")

    assert response.status_code == codes.UNAUTHORIZED
    assert response.json()["message"] == UnauthorizedError.message


def test_forbidden_domain_error_returns_verbose_403() -> None:
    response = get_response("/forbidden")

    assert response.status_code == codes.FORBIDDEN
    assert response.json()["message"] == ForbiddenError.message


def test_quota_domain_error_returns_verbose_429() -> None:
    response = get_response("/question-quota")

    assert response.status_code == codes.TOO_MANY_REQUESTS
    assert response.json()["message"] == QuestionSuggestionQuotaExceededError.message


def test_import_domain_error_returns_verbose_400_with_nested_errors() -> None:
    response = get_response("/question-import")

    assert response.status_code == codes.BAD_REQUEST
    assert response.json()["message"] == QuestionQueueImportInvalidError.message
    assert response.json()["nested_errors"] == [
        {
            "code": "client_error",
            "type": "bad_request",
            "message": "Row 2 question must not be blank.",
            "location": "body",
            "attr": "file.row.2",
        },
    ]


def test_python_error_still_uses_verbose_catch_all_handler() -> None:
    response = get_response("/python-error")

    assert response.status_code == codes.INTERNAL_SERVER_ERROR
    assert response.json()["message"] == "plain python error"


def test_domain_errors_are_registered_with_single_data_driven_handler() -> None:
    handlers = get_litestar_exception_handlers()

    assert handlers[DomainError] is exception_handlers.domain_to_verbose_response_handler
    for domain_error_type in exception_handlers.DOMAIN_ERROR_MAPPING:
        assert domain_error_type not in handlers


def test_domain_error_verbose_exception_mapping() -> None:
    expected_mapping = {
        EntryNotFoundError: NotFoundHTTPException,
        UnauthorizedError: UnauthorizedHTTPException,
        ForbiddenError: ForbiddenHTTPException,
        InvalidFileDataError: BadRequestHTTPException,
        FileStorageInternalError: InternalServerErrorHTTPException,
        QuestionSuggestionQuotaExceededError: TooManyRequestsHTTPException,
        QuestionQueueImportInvalidError: BadRequestHTTPException,
    }
    assert expected_mapping == exception_handlers.DOMAIN_ERROR_MAPPING


def get_response(path: str) -> Response:
    app = Litestar(
        route_handlers=list(exception_route_handlers()),
        exception_handlers=get_litestar_exception_handlers(),
    )
    with TestClient(app) as client:
        return client.get(path)


def exception_route_handlers() -> Sequence[ControllerRouterHandler]:
    return (
        raise_entry_not_found,
        raise_unauthorized,
        raise_forbidden,
        raise_question_quota,
        raise_question_import,
        raise_python_error,
    )
