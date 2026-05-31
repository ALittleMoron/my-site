from typing import Any, Self

from entrypoints.litestar.api.i18n.schemas import LanguagesResponseSchema
from performance.http import PerformanceApiClient


class FakeResponse:
    def __init__(self, *, status_code: int, payload: object) -> None:
        self.status_code = status_code
        self.payload = payload
        self.failure_message: str | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def json(self) -> object:
        return self.payload

    def failure(self, message: str) -> None:
        self.failure_message = message


class FakeHttpClient:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def get(self, path: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"path": path, **kwargs})
        return self.response


class TestPerformanceApiClient:
    def test_get_without_validation_delegates_to_locust_client(self) -> None:
        response = FakeResponse(status_code=200, payload={})
        client = FakeHttpClient(response)
        api_client = PerformanceApiClient(client=client, validate_responses=False)

        result = api_client.get(
            "/api/i18n/languages",
            name="GET /api/i18n/languages",
            schema_type=LanguagesResponseSchema,
        )

        assert result is None
        assert client.calls == [
            {
                "path": "/api/i18n/languages",
                "name": "GET /api/i18n/languages",
            },
        ]

    def test_get_with_validation_returns_response_schema(self) -> None:
        response = FakeResponse(
            status_code=200,
            payload={
                "defaultLanguage": "ru",
                "languages": [{"code": "ru", "label": "Русский"}],
            },
        )
        client = FakeHttpClient(response)
        api_client = PerformanceApiClient(client=client, validate_responses=True)

        result = api_client.get(
            "/api/i18n/languages",
            name="GET /api/i18n/languages",
            schema_type=LanguagesResponseSchema,
        )

        assert isinstance(result, LanguagesResponseSchema)
        assert client.calls == [
            {
                "path": "/api/i18n/languages",
                "name": "GET /api/i18n/languages",
                "catch_response": True,
            },
        ]

    def test_get_with_validation_marks_bad_status_as_failure(self) -> None:
        response = FakeResponse(status_code=500, payload={})
        client = FakeHttpClient(response)
        api_client = PerformanceApiClient(client=client, validate_responses=True)

        result = api_client.get(
            "/api/i18n/languages",
            name="GET /api/i18n/languages",
            schema_type=LanguagesResponseSchema,
        )

        assert result is None
        assert response.failure_message == "GET /api/i18n/languages returned 500"

    def test_get_with_validation_marks_schema_error_as_failure(self) -> None:
        response = FakeResponse(status_code=200, payload={})
        client = FakeHttpClient(response)
        api_client = PerformanceApiClient(client=client, validate_responses=True)

        result = api_client.get(
            "/api/i18n/languages",
            name="GET /api/i18n/languages",
            schema_type=LanguagesResponseSchema,
        )

        assert result is None
        assert response.failure_message == "LanguagesResponseSchema validation failed"
