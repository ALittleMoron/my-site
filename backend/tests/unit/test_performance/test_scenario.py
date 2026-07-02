from typing import Any, Self

import pytest

from core.i18n.enums import LanguageEnum
from performance.locust import scenario as scenario_module
from performance.locust.scenario import PublicSiteScenario
from performance.locust.settings import LocustScenarioSettings


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
        self.post_status_code = 204
        self.responses: list[FakeResponse] = []

    def get(self, path: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"path": path, **kwargs})
        return FakeResponse(status_code=200, payload=self._payload_for_path(path))

    def post(self, path: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"path": path, **kwargs})
        response = FakeResponse(status_code=self.post_status_code, payload={})
        self.responses.append(response)
        return response

    def _payload_for_path(self, path: str) -> object:
        payload: object = {}
        if path.startswith("/api/competency-matrix/sheets"):
            payload = {
                "sheets": [
                    {"key": "python", "name": "Python"},
                    {"key": "backend", "name": "Backend"},
                ],
            }
        elif path.startswith("/api/articles/detail/"):
            payload = article_detail_payload(slug="seeded-article")
        elif path.startswith("/api/articles"):
            payload = {
                "totalCount": 1,
                "totalPages": 1,
                "articles": [article_summary_payload(slug="seeded-article")],
            }
        elif path.startswith("/api/competency-matrix/items/public/"):
            payload = matrix_item_detail_payload(slug="matrix-q-001-python")
        elif path.startswith("/api/competency-matrix/items"):
            sheet_key = "backend" if "sheetKey=backend" in path else "python"
            payload = matrix_items_payload(sheet_key=sheet_key)
        return payload


def article_summary_payload(*, slug: str) -> dict[str, object]:
    return {
        "id": "10000000-0000-4000-8000-000000000001",
        "title": "Seeded article",
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


def article_detail_payload(*, slug: str) -> dict[str, object]:
    payload = article_summary_payload(slug=slug)
    payload.update(
        {
            "content": "# Seeded article\n\nA seeded article detail.",
            "createdAt": "2026-02-10T09:30:00+00:00",
            "translations": {
                "ru": {
                    "title": "Тестовая статья",
                    "content": "# Тестовая статья",
                    "folder": "Производительность",
                },
                "en": {
                    "title": "Seeded article",
                    "content": "# Seeded article",
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
                                        "slug": slug,
                                        "question": "How do you test this?",
                                        "interviewFrequency": "often",
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
        "slug": slug,
        "question": "How do you test this?",
        "interviewFrequency": "often",
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
    def scenario_settings(
        self,
        *,
        include_matrix_suggestions: bool,
    ) -> LocustScenarioSettings:
        return LocustScenarioSettings(
            _env_file=None,
            language=LanguageEnum.EN,
            include_spa=False,
            include_matrix_suggestions=include_matrix_suggestions,
            validate_responses=True,
        )

    def test_matrix_requests_include_required_language_and_sheet_key(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(scenario_module, "choice", lambda values: values[0])

        client = FakeHttpClient()
        scenario = PublicSiteScenario(
            client=client,
            settings=self.scenario_settings(include_matrix_suggestions=False),
        )

        assert client.calls[0] == {
            "path": "/api/competency-matrix/sheets?language=en",
            "name": "GET /api/competency-matrix/sheets",
            "catch_response": True,
        }

        client.calls.clear()

        scenario.matrix_sheets_task()
        scenario.matrix_items()

        assert client.calls == [
            {
                "path": "/api/competency-matrix/sheets?language=en",
                "name": "GET /api/competency-matrix/sheets",
                "catch_response": True,
            },
            {
                "path": "/api/competency-matrix/items?sheetKey=python&language=en",
                "name": "GET /api/competency-matrix/items",
                "catch_response": True,
            },
        ]

    def test_public_data_discovery_fetches_seeded_article_and_matrix_slugs(self) -> None:
        client = FakeHttpClient()
        scenario = PublicSiteScenario(
            client=client,
            settings=self.scenario_settings(include_matrix_suggestions=False),
        )

        assert scenario.article_slugs == ["seeded-article"]
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
                "path": "/api/articles?page=1&pageSize=100&language=en",
                "name": "GET /api/articles",
                "catch_response": True,
            },
            {
                "path": "/api/competency-matrix/items?sheetKey=python&language=en",
                "name": "GET /api/competency-matrix/items",
                "catch_response": True,
            },
            {
                "path": "/api/competency-matrix/items?sheetKey=backend&language=en",
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
            settings=self.scenario_settings(include_matrix_suggestions=False),
        )
        client.calls.clear()

        scenario.article_detail()
        scenario.matrix_item_detail()

        assert client.calls == [
            {
                "path": "/api/articles/detail/seeded-article?language=en",
                "name": "GET /api/articles/detail/:slug",
                "catch_response": True,
            },
            {
                "path": "/api/competency-matrix/items/public/matrix-q-001-python?language=en",
                "name": "GET /api/competency-matrix/items/public/:slug",
                "catch_response": True,
            },
        ]

    def test_matrix_question_suggestion_is_skipped_when_disabled(self) -> None:
        client = FakeHttpClient()
        scenario = PublicSiteScenario(
            client=client,
            settings=self.scenario_settings(include_matrix_suggestions=False),
        )
        client.calls.clear()

        scenario.matrix_question_suggestion()

        assert client.calls == []

    def test_matrix_question_suggestion_posts_when_enabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(scenario_module, "choice", lambda values: values[0])

        client = FakeHttpClient()
        scenario = PublicSiteScenario(
            client=client,
            settings=self.scenario_settings(include_matrix_suggestions=True),
        )
        client.calls.clear()

        scenario.matrix_question_suggestion()

        assert client.calls == [
            {
                "path": "/api/competency-matrix/question-suggestions",
                "name": "POST /api/competency-matrix/question-suggestions",
                "json": {"question": "Locust matrix suggestion en-1", "sheet": "python"},
                "catch_response": True,
            },
        ]
        assert client.responses[-1].failure_message is None

    def test_matrix_question_suggestion_accepts_expected_rate_limit(self) -> None:
        client = FakeHttpClient()
        client.post_status_code = 429
        scenario = PublicSiteScenario(
            client=client,
            settings=self.scenario_settings(include_matrix_suggestions=True),
        )
        client.calls.clear()

        scenario.matrix_question_suggestion()

        assert client.responses[-1].failure_message is None
