from verbose_http_exceptions import BadRequestHTTPException, TooManyRequestsHTTPException

from core.exceptions import EntryNotFoundError


class CompetencyMatrixItemNotFoundError(EntryNotFoundError):
    message = "Competency matrix item not found"


class QueuedCompetencyMatrixQuestionNotFoundError(EntryNotFoundError):
    message = "Queued competency matrix question not found"


class QuestionSuggestionQuotaExceededError(TooManyRequestsHTTPException):
    message = "Question suggestion daily quota exceeded"


class QuestionQueueImportIssue(BadRequestHTTPException):
    def __init__(self, *, message: str, row_number: int | None) -> None:
        self.row_number = row_number
        super().__init__(
            message=message,
            location="body",
            attr_name=self.attr_name,
        )

    @property
    def attr_name(self) -> str:
        if self.row_number is None:
            return "file"
        return f"file.row.{self.row_number}"


class QuestionQueueImportInvalidError(BadRequestHTTPException):
    message = "Question queue import file is invalid."

    def __init__(self, *, issues: list[QuestionQueueImportIssue]) -> None:
        self.issues = tuple(issues)
        super().__init__(*self.issues, message=self.message)
