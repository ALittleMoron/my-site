from verbose_http_exceptions import UnauthorizedHTTPException

from core.exceptions import EntryNotFoundError


class UnauthorizedError(UnauthorizedHTTPException):
    message = "Unauthorized error"


class UserNotFoundError(EntryNotFoundError):
    message = "User not found"
