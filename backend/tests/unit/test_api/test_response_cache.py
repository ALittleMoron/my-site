from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, cast

from litestar.config.response_cache import CACHE_FOREVER
from litestar.stores.base import Store

from entrypoints.litestar.api.competency_matrix.endpoints import CompetencyMatrixApiController
from entrypoints.litestar.api.healthcheck.endpoints import HealthcheckController
from entrypoints.litestar.api.i18n.endpoints import I18nApiController
from entrypoints.litestar.api.notes.endpoints import NotesApiController
from entrypoints.litestar.guards import draft_content_access_guard
from entrypoints.litestar.response_cache import (
    ResponseCacheDomain,
    ResponseCacheDomainStore,
)
from infra.config.constants import constants
from infra.config.settings import settings


@dataclass
class FakeStore:
    values: dict[str, bytes] = field(default_factory=dict)
    set_calls: list[tuple[str, str | bytes, int | timedelta | None]] = field(default_factory=list)
    delete_calls: list[str] = field(default_factory=list)
    delete_all_count: int = 0

    async def set(
        self,
        key: str,
        value: str | bytes,
        expires_in: int | timedelta | None = None,
    ) -> None:
        self.set_calls.append((key, value, expires_in))
        self.values[key] = value if isinstance(value, bytes) else value.encode()

    async def get(self, key: str, renew_for: int | timedelta | None = None) -> bytes | None:
        return self.values.get(key)

    async def delete(self, key: str) -> None:
        self.delete_calls.append(key)
        self.values.pop(key, None)

    async def delete_all(self) -> None:
        self.delete_all_count += 1
        self.values.clear()

    async def exists(self, key: str) -> bool:
        return key in self.values

    async def expires_in(self, key: str) -> int | None:
        return 60 if key in self.values else None


class FakeQueryParams:
    def __init__(self, values: dict[str, Any]) -> None:
        self._values = values

    def dict(self) -> dict[str, Any]:
        return self._values


class FakeUrl:
    path = "/api/notes"


class FakeRequest:
    method = "GET"
    url = FakeUrl()
    query_params = FakeQueryParams({"language": "ru", "page": "1"})


class TestResponseCacheDomainStore:
    async def test_routes_values_to_domain_store(self) -> None:
        notes_store = FakeStore()
        matrix_store = FakeStore()
        store = ResponseCacheDomainStore(
            stores={
                ResponseCacheDomain.NOTES: cast("Store", notes_store),
                ResponseCacheDomain.COMPETENCY_MATRIX: cast("Store", matrix_store),
            },
        )

        await store.set("notes:GET/api/noteslanguage=rupage=1", b"notes")
        await store.set("competency_matrix:GET/api/competency-matrix/sheetslanguage=ru", b"matrix")

        assert await notes_store.get("GET/api/noteslanguage=rupage=1") == b"notes"
        assert await matrix_store.get("GET/api/competency-matrix/sheetslanguage=ru") == b"matrix"
        assert await store.get("notes:GET/api/noteslanguage=rupage=1") == b"notes"

    async def test_deletes_only_requested_domain(self) -> None:
        notes_store = FakeStore(values={"GET/api/notes": b"notes"})
        matrix_store = FakeStore(values={"GET/api/competency-matrix/sheets": b"matrix"})
        store = ResponseCacheDomainStore(
            stores={
                ResponseCacheDomain.NOTES: cast("Store", notes_store),
                ResponseCacheDomain.COMPETENCY_MATRIX: cast("Store", matrix_store),
            },
        )

        await store.delete_domain(ResponseCacheDomain.NOTES)

        assert notes_store.delete_all_count == 1
        assert notes_store.values == {}
        assert matrix_store.delete_all_count == 0
        assert matrix_store.values == {"GET/api/competency-matrix/sheets": b"matrix"}


class TestResponseCacheKeyBuilder:
    def test_builds_domain_prefixed_sorted_litestar_key(self) -> None:
        cache_key_builder = ResponseCacheDomain.NOTES.cache_key_builder

        cache_key = cache_key_builder(cast("Any", FakeRequest()))

        assert cache_key == "notes:GET/api/noteslanguage=ru&page=1"

    def test_uses_configured_domain_separator(self) -> None:
        cache_key = ResponseCacheDomain.NOTES.cache_key_builder(cast("Any", FakeRequest()))

        assert constants.response_cache.domain_key_separator in cache_key


class TestResponseCacheRouteConfiguration:
    def test_safe_notes_get_handlers_use_notes_cache(self) -> None:
        for handler_name in ("list_notes", "get_note", "list_tags", "search_tags"):
            handler = getattr(NotesApiController, handler_name)

            assert handler.cache == settings.app.get_cache_duration(CACHE_FOREVER)
            assert handler.cache_key_builder is not None
            assert handler.cache_key_builder(cast("Any", FakeRequest())).startswith("notes:")

    def test_dynamic_notes_get_handlers_are_not_cached(self) -> None:
        for handler_name in ("list_notes_tree", "get_public_stats", "get_stats"):
            assert getattr(NotesApiController, handler_name).cache is False

    def test_draft_notes_get_handlers_use_pre_cache_guard(self) -> None:
        for handler_name in ("list_notes", "get_note"):
            assert draft_content_access_guard in getattr(NotesApiController, handler_name).guards

    def test_competency_matrix_get_handlers_use_matrix_cache(self) -> None:
        for handler_name in (
            "list_competency_matrix_sheet",
            "search_competency_matrix_resources",
            "list_competency_matrix_items",
            "get_competency_matrix_item",
        ):
            handler = getattr(CompetencyMatrixApiController, handler_name)

            assert handler.cache == settings.app.get_cache_duration(CACHE_FOREVER)
            assert handler.cache_key_builder is not None
            assert handler.cache_key_builder(cast("Any", FakeRequest())).startswith(
                "competency_matrix:",
            )

    def test_draft_matrix_get_handlers_use_pre_cache_guard(self) -> None:
        for handler_name in ("list_competency_matrix_items", "get_competency_matrix_item"):
            assert (
                draft_content_access_guard
                in getattr(CompetencyMatrixApiController, handler_name).guards
            )

    def test_i18n_get_handlers_use_i18n_cache(self) -> None:
        for handler_name in ("list_languages", "get_bundle"):
            handler = getattr(I18nApiController, handler_name)

            assert handler.cache == settings.app.get_cache_duration(CACHE_FOREVER)
            assert handler.cache_key_builder is not None
            assert handler.cache_key_builder(cast("Any", FakeRequest())).startswith("i18n:")

    def test_healthcheck_uses_domain_cache_key(self) -> None:
        handler = HealthcheckController.health

        assert handler.cache == settings.app.get_cache_duration(1)
        assert handler.cache_key_builder is not None
        assert handler.cache_key_builder(cast("Any", FakeRequest())).startswith("healthcheck:")
