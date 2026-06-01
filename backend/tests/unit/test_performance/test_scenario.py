from typing import Any, Self

from performance.locust.scenario import PublicSiteScenario


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
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def get(self, path: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"path": path, **kwargs})
        return FakeResponse(status_code=200, payload=self._payload_for_path(path))

    def _payload_for_path(self, path: str) -> object:
        if path.startswith("/api/competency-matrix/sheets"):
            return {"sheets": [{"key": "python", "name": "Python"}]}
        if path.startswith("/api/notes"):
            return {"totalCount": 0, "totalPages": 0, "notes": []}
        if path.startswith("/api/competency-matrix/items"):
            return {"sheetKey": "python", "sheet": "Python", "sections": []}
        if path.startswith("/api/competency-matrix/resources/search"):
            return {"resources": []}
        return {}


class TestPublicSiteScenario:
    def test_matrix_requests_include_required_language_and_sheet_key(self) -> None:
        client = FakeHttpClient()
        scenario = PublicSiteScenario(
            client=client,
            environ={
                "PERFORMANCE_LANGUAGE": "en",
                "PERFORMANCE_INCLUDE_SPA": "false",
                "PERFORMANCE_VALIDATE_RESPONSES": "true",
            },
        )

        assert client.calls[0] == {
            "path": "/api/competency-matrix/sheets?language=en",
            "name": "GET /api/competency-matrix/sheets",
            "catch_response": True,
        }

        client.calls.clear()

        scenario.matrix_sheets_task()
        scenario.matrix_items()
        scenario.matrix_resources_search()

        assert client.calls == [
            {
                "path": "/api/competency-matrix/sheets?language=en",
                "name": "GET /api/competency-matrix/sheets",
                "catch_response": True,
            },
            {
                "path": "/api/competency-matrix/items"
                "?sheetKey=python&onlyPublished=true&language=en",
                "name": "GET /api/competency-matrix/items",
                "catch_response": True,
            },
            {
                "path": "/api/competency-matrix/resources/search"
                "?searchName=python&limit=5&language=en",
                "name": "GET /api/competency-matrix/resources/search",
                "catch_response": True,
            },
        ]
