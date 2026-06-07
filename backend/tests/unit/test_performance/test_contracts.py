import pytest

from core.i18n.enums import LanguageEnum
from entrypoints.litestar.api.i18n.schemas import LanguagesResponseSchema
from performance.locust.contracts import validate_response_payload


class TestPerformanceContracts:
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
