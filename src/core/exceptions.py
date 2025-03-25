from verbose_http_exceptions import NotFoundHTTPException


class EntryNotFoundError(NotFoundHTTPException):
    message = "Entry not found"
