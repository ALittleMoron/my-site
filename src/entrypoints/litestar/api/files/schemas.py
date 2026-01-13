from typing import Annotated

from pydantic import Field, HttpUrl

from core.files.schemas import PresignPutObject
from entrypoints.litestar.api.schemas import CamelCaseSchema


class FilePresignPutResponseSchema(CamelCaseSchema):
    upload_url: Annotated[
        HttpUrl,
        Field(
            title="Ссылка для загрузки",
            description="Ссылка для загрузки файла",
            examples=["https://example.com/path/to/file"],
        ),
    ]
    access_url: Annotated[
        HttpUrl,
        Field(
            title="Ссылка для доступа",
            description="Ссылка для доступа к загруженному файлу",
            examples=["https://example.com/path/to/file"],
        ),
    ]

    @classmethod
    def from_schema(cls, *, schema: PresignPutObject) -> "FilePresignPutResponseSchema":
        return cls(
            upload_url=HttpUrl(schema.upload_url),
            access_url=HttpUrl(schema.access_url),
        )
