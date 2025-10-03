from dataclasses import dataclass

from core.files.exceptions import ContentTypeNotAllowedError
from core.files.types import Namespace


@dataclass(frozen=True, slots=True, kw_only=True)
class FileUploadResult:
    url: str
    bucket: str
    object_name: str
    size: int


@dataclass(frozen=True, slots=True, kw_only=True)
class PresignPutObjectParams:
    content_type: str
    folder: str
    namespace: Namespace

    def validate_content_type(self, allowed_types: set[str] | list[str] | tuple[str, ...]) -> None:
        if self.content_type not in allowed_types:
            raise ContentTypeNotAllowedError(template_vars={"content_type": self.content_type})


@dataclass(frozen=True, slots=True, kw_only=True)
class PresignPutObject:
    upload_url: str
    access_url: str
