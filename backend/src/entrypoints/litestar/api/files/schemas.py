from typing import Annotated, Self

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
    def from_domain_schema(cls, *, schema: PresignPutObject) -> Self:
        return cls(
            upload_url=HttpUrl(schema.upload_url),
            access_url=HttpUrl(schema.access_url),
        )
