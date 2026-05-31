import pytest

from core.i18n.enums import LanguageEnum
from entrypoints.litestar.api.i18n.schemas import LanguagesResponseSchema
from performance.locust.contracts import (
    performance_language_from_environment,
    validate_response_payload,
)


class TestPerformanceContracts:
    def test_performance_language_from_environment_requires_language(self) -> None:
        with pytest.raises(ValueError, match="PERFORMANCE_LANGUAGE"):
            performance_language_from_environment({})

    def test_performance_language_from_environment_validates_language_enum(self) -> None:
        with pytest.raises(ValueError, match="PERFORMANCE_LANGUAGE must be one of"):
            performance_language_from_environment({"PERFORMANCE_LANGUAGE": "de"})

    def test_performance_language_from_environment_returns_language_enum(self) -> None:
        assert (
            performance_language_from_environment({"PERFORMANCE_LANGUAGE": "ru"}) == LanguageEnum.RU
        )

    def test_validate_response_payload_returns_schema(self) -> None:
        schema = validate_response_payload(
            payload={
                "defaultLanguage": "ru",
                "languages": [
                    {
                        "code": "ru",
                        "label": "Русский",
                    },
                ],
            },
            schema_type=LanguagesResponseSchema,
        )

        assert schema.default_language == LanguageEnum.RU
        assert schema.languages[0].code == LanguageEnum.RU

    def test_validate_response_payload_raises_readable_error(self) -> None:
        with pytest.raises(ValueError, match="LanguagesResponseSchema validation failed"):
            validate_response_payload(payload={}, schema_type=LanguagesResponseSchema)
