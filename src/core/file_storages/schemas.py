from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class FileUploadResult:
    url: str
    bucket: str
    object_name: str
    size: int
