from string import Template

from verbose_http_exceptions import BadRequestHTTPException, InternalServerErrorHTTPException


class InvalidFileDataError(BadRequestHTTPException):
    message = "File data is invalid."


class ContentTypeNotAllowedError(InvalidFileDataError):
    message = "Content type is not allowed."
    template = Template("Content type '$content_type' is not allowed.")


class NamespaceNotAllowedError(InvalidFileDataError):
    message = "Namespace not allowed."
    template = Template("Namespace '$content_type' is not allowed.")


class FileStorageInternalError(InternalServerErrorHTTPException):
    message = "File storage error"
