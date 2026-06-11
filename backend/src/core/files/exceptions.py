from core.exceptions import DomainError


class InvalidFileDataError(DomainError):
    message = "File data is invalid."


class ContentTypeNotAllowedError(InvalidFileDataError):
    message = "Content type is not allowed."

    def __init__(self, *, content_type: str) -> None:
        self.message = f"Content type '{content_type}' is not allowed."
        super().__init__()


class NamespaceNotAllowedError(InvalidFileDataError):
    message = "Namespace not allowed."

    def __init__(self, *, namespace: str) -> None:
        self.message = f"Namespace '{namespace}' is not allowed."
        super().__init__()


class FileStorageInternalError(DomainError):
    message = "File storage error"

    def __init__(self, *, message: str) -> None:
        self.message = message
        super().__init__()
