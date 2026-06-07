from verbose_http_exceptions import TooManyRequestsHTTPException

from core.exceptions import EntryNotFoundError


class CompetencyMatrixItemNotFoundError(EntryNotFoundError):
    message = "Competency matrix item not found"


class QueuedCompetencyMatrixQuestionNotFoundError(EntryNotFoundError):
    message = "Queued competency matrix question not found"


class QuestionSuggestionQuotaExceededError(TooManyRequestsHTTPException):
    message = "Question suggestion daily quota exceeded"
