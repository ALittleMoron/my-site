from collections.abc import Mapping

from pydantic import BaseModel, ValidationError

from core.i18n.enums import LanguageEnum


def performance_language_from_environment(environ: Mapping[str, str]) -> LanguageEnum:
    try:
        raw_language = environ["PERFORMANCE_LANGUAGE"]
    except KeyError as exc:
        msg = "PERFORMANCE_LANGUAGE is required"
        raise ValueError(msg) from exc
    try:
        return LanguageEnum(raw_language)
    except ValueError as exc:
        supported_languages = ", ".join(language.value for language in LanguageEnum)
        msg = f"PERFORMANCE_LANGUAGE must be one of: {supported_languages}"
        raise ValueError(msg) from exc


def validate_response_payload[ResponseSchemaT: BaseModel](
    *,
    payload: object,
    schema_type: type[ResponseSchemaT],
) -> ResponseSchemaT:
    try:
        return schema_type.model_validate(payload)
    except ValidationError as exc:
        msg = f"{schema_type.__name__} validation failed"
        raise ValueError(msg) from exc
