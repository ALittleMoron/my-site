from verbose_http_exceptions import InternalServerErrorHTTPException


class FileStorageInternalError(InternalServerErrorHTTPException):
    message = "File storage error"
