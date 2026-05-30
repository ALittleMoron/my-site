from typing import Annotated, Self

from pydantic import Field

from core.i18n.enums import LanguageEnum
from entrypoints.litestar.api.schemas import CamelCaseSchema


class LanguageResponseSchema(CamelCaseSchema):
    code: Annotated[LanguageEnum, Field(title="Код языка")]
    label: Annotated[str, Field(title="Название языка")]

    @classmethod
    def from_language(cls, *, language: LanguageEnum, label: str) -> Self:
        return cls(code=language, label=label)


class LanguagesResponseSchema(CamelCaseSchema):
    default_language: Annotated[LanguageEnum, Field(title="Язык по умолчанию")]
    languages: Annotated[list[LanguageResponseSchema], Field(title="Доступные языки")]


class I18nBundleResponseSchema(CamelCaseSchema):
    language: Annotated[LanguageEnum, Field(title="Язык")]
    messages: Annotated[dict[str, str], Field(title="Переводы")]
