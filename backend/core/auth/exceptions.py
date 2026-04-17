from core.exceptions import EntryNotFoundError
from verbose_http_exceptions import ForbiddenHTTPException, UnauthorizedHTTPException


class UnauthorizedError(UnauthorizedHTTPException):
    message = "Unauthorized error"


class ForbiddenError(ForbiddenHTTPException):
    message = "Forbidden error"


class UserNotFoundError(EntryNotFoundError):
    message = "User not found"
