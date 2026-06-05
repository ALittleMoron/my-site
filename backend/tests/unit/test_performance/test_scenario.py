from typing import Any, Self

import pytest

from performance.locust import scenario as scenario_module
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
        payload: object = {}
        if path.startswith("/api/competency-matrix/sheets"):
            payload = {
                "sheets": [
                    {"key": "python", "name": "Python"},
                    {"key": "backend", "name": "Backend"},
                ],
            }
        elif path.startswith("/api/notes/detail/"):
            payload = note_detail_payload(slug="seeded-note")
        elif path.startswith("/api/notes"):
            payload = {
                "totalCount": 1,
                "totalPages": 1,
                "notes": [note_summary_payload(slug="seeded-note")],
            }
        elif path.startswith("/api/competency-matrix/items/public/"):
            payload = matrix_item_detail_payload(slug="matrix-q-001-python")
        elif path.startswith("/api/competency-matrix/items"):
            sheet_key = "backend" if "sheetKey=backend" in path else "python"
            payload = matrix_items_payload(sheet_key=sheet_key)
        elif path.startswith("/api/competency-matrix/resources/search"):
            payload = {"resources": []}
        return payload


def note_summary_payload(*, slug: str) -> dict[str, object]:
    return {
        "id": "10000000-0000-4000-8000-000000000001",
        "title": "Seeded note",
        "slug": slug,
        "folder": "Performance",
        "authorUsername": "admin",
        "publishedAt": "2026-03-01T10:00:00+00:00",
        "publishStatus": "Published",
        "updatedAt": "2026-05-25T20:00:00+00:00",
        "excerpt": "Seeded detail content",
        "metadata": {
            "seoTitleRu": None,
            "seoTitleEn": None,
            "seoDescriptionRu": None,
            "seoDescriptionEn": None,
            "coverImageUrl": None,
            "coverImageAltRu": None,
            "coverImageAltEn": None,
        },
        "tags": [],
    }


def note_detail_payload(*, slug: str) -> dict[str, object]:
    payload = note_summary_payload(slug=slug)
    payload.update(
        {
            "content": "# Seeded note\n\nA seeded note detail.",
            "createdAt": "2026-02-10T09:30:00+00:00",
            "translations": {
                "ru": {
                    "title": "Тестовая заметка",
                    "content": "# Тестовая заметка",
                    "folder": "Производительность",
                },
                "en": {
                    "title": "Seeded note",
                    "content": "# Seeded note",
                    "folder": "Performance",
                },
            },
        },
    )
    return payload


def matrix_items_payload(*, sheet_key: str) -> dict[str, object]:
    slug = f"matrix-q-001-{sheet_key}"
    return {
        "sheetKey": sheet_key,
        "sheet": sheet_key.title(),
        "sections": [
            {
                "section": "Basics",
                "subsections": [
                    {
                        "subsection": "Performance",
                        "grades": [
                            {
                                "grade": "Junior",
                                "items": [
                                    {
                                        "id": 1,
                                        "slug": slug,
                                        "question": "How do you test this?",
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }


def matrix_item_detail_payload(*, slug: str) -> dict[str, object]:
    return {
        "id": 1,
        "slug": slug,
        "question": "How do you test this?",
        "answer": "Use a realistic seeded scenario.",
        "interviewExpectedAnswer": "Name the data, threshold, and rollback path.",
        "sheetKey": "python",
        "sheet": "Python",
        "grade": "Junior",
        "section": "Basics",
        "subsection": "Performance",
        "publishStatus": "Published",
        "resources": [],
        "translations": {
            "ru": {
                "question": "Как проверить это?",
                "answer": "Через реалистичный seed.",
                "interviewExpectedAnswer": "Назвать данные, порог и откат.",
                "sheet": "Питон",
                "section": "Основы",
                "subsection": "Производительность",
            },
            "en": {
                "question": "How do you test this?",
                "answer": "Use a realistic seeded scenario.",
                "interviewExpectedAnswer": "Name the data, threshold, and rollback path.",
                "sheet": "Python",
                "section": "Basics",
                "subsection": "Performance",
            },
        },
    }


class TestPublicSiteScenario:
    def test_matrix_requests_include_required_language_and_sheet_key(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(scenario_module, "choice", lambda values: values[0])

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

    def test_public_data_discovery_fetches_seeded_note_and_matrix_slugs(self) -> None:
        client = FakeHttpClient()
        scenario = PublicSiteScenario(
            client=client,
            environ={
                "PERFORMANCE_LANGUAGE": "en",
                "PERFORMANCE_INCLUDE_SPA": "false",
                "PERFORMANCE_VALIDATE_RESPONSES": "true",
            },
        )

        assert scenario.note_slugs == ["seeded-note"]
        assert scenario.matrix_item_slugs == [
            "matrix-q-001-python",
            "matrix-q-001-backend",
        ]
        assert client.calls[:4] == [
            {
                "path": "/api/competency-matrix/sheets?language=en",
                "name": "GET /api/competency-matrix/sheets",
                "catch_response": True,
            },
            {
                "path": "/api/notes?page=1&pageSize=100&onlyPublished=true&language=en",
                "name": "GET /api/notes",
                "catch_response": True,
            },
            {
                "path": "/api/competency-matrix/items"
                "?sheetKey=python&onlyPublished=true&language=en",
                "name": "GET /api/competency-matrix/items",
                "catch_response": True,
            },
            {
                "path": "/api/competency-matrix/items"
                "?sheetKey=backend&onlyPublished=true&language=en",
                "name": "GET /api/competency-matrix/items",
                "catch_response": True,
            },
        ]

    def test_detail_tasks_use_discovered_seeded_slugs(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(scenario_module, "choice", lambda values: values[0])

        client = FakeHttpClient()
        scenario = PublicSiteScenario(
            client=client,
            environ={
                "PERFORMANCE_LANGUAGE": "en",
                "PERFORMANCE_INCLUDE_SPA": "false",
                "PERFORMANCE_VALIDATE_RESPONSES": "true",
            },
        )
        client.calls.clear()

        scenario.note_detail()
        scenario.matrix_item_detail()

        assert client.calls == [
            {
                "path": "/api/notes/detail/seeded-note?onlyPublished=true&language=en",
                "name": "GET /api/notes/detail/:slug",
                "catch_response": True,
            },
            {
                "path": "/api/competency-matrix/items/public/matrix-q-001-python?language=en",
                "name": "GET /api/competency-matrix/items/public/:slug",
                "catch_response": True,
            },
        ]
