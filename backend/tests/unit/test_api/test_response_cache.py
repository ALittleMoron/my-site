from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, cast

import click
import pytest
from litestar.exceptions import ImproperlyConfiguredException
from litestar.stores.base import Store

from entrypoints.litestar.api.competency_matrix.endpoints import (
    AdminCompetencyMatrixApiController,
    PublicCompetencyMatrixApiController,
)
from entrypoints.litestar.api.healthcheck.endpoints import HealthcheckController
from entrypoints.litestar.api.i18n.endpoints import I18nApiController
from entrypoints.litestar.api.notes.endpoints import (
    AdminNotesApiController,
    PublicNotesApiController,
)
from entrypoints.litestar.cli.plugins import CLIPlugin
from entrypoints.litestar.response_cache import (
    ResponseCacheDomain,
    ResponseCacheDomainStore,
    invalidate_all_response_cache_domains,
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


class FakeStores:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.requested_names: list[str] = []

    def get(self, name: str) -> Store:
        self.requested_names.append(name)
        return self.store


class FakeApp:
    def __init__(self, store: Store) -> None:
        self.stores = FakeStores(store=store)


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


class TestInvalidateAllResponseCacheDomains:
    async def test_deletes_all_domain_stores_when_cache_is_enabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        notes_store = FakeStore(values={"GET/api/notes": b"notes"})
        matrix_store = FakeStore(values={"GET/api/competency-matrix/sheets": b"matrix"})
        domain_store = ResponseCacheDomainStore(
            stores={
                ResponseCacheDomain.NOTES: cast("Store", notes_store),
                ResponseCacheDomain.COMPETENCY_MATRIX: cast("Store", matrix_store),
            },
        )
        app = FakeApp(store=cast("Store", domain_store))
        monkeypatch.setattr(settings.app, "use_cache", True)

        await invalidate_all_response_cache_domains(app=cast("Any", app))

        assert app.stores.requested_names == [constants.response_cache.store_name]
        assert notes_store.delete_all_count == 1
        assert matrix_store.delete_all_count == 1
        assert notes_store.values == {}
        assert matrix_store.values == {}

    async def test_noops_when_cache_is_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        store = FakeStore(values={"GET/api/notes": b"notes"})
        app = FakeApp(store=cast("Store", store))
        monkeypatch.setattr(settings.app, "use_cache", False)

        await invalidate_all_response_cache_domains(app=cast("Any", app))

        assert app.stores.requested_names == []
        assert store.delete_all_count == 0
        assert store.values == {"GET/api/notes": b"notes"}

    async def test_rejects_non_domain_routed_store(self, monkeypatch: pytest.MonkeyPatch) -> None:
        app = FakeApp(store=cast("Store", FakeStore()))
        monkeypatch.setattr(settings.app, "use_cache", True)

        with pytest.raises(ImproperlyConfiguredException):
            await invalidate_all_response_cache_domains(app=cast("Any", app))


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
        for handler_name in ("list_notes", "list_notes_tree", "get_note", "list_tags"):
            handler = getattr(PublicNotesApiController, handler_name)

            assert handler.cache == settings.app.get_cache_duration(
                constants.response_cache.default_ttl_seconds,
            )
            assert handler.cache_key_builder is not None
            assert handler.cache_key_builder(cast("Any", FakeRequest())).startswith("notes:")

    def test_dynamic_notes_get_handlers_are_not_cached(self) -> None:
        for handler_name in ("get_public_stats",):
            assert getattr(PublicNotesApiController, handler_name).cache is False

    def test_admin_notes_get_handlers_are_not_cached(self) -> None:
        for handler_name in (
            "list_notes",
            "list_notes_tree",
            "get_note",
            "get_stats",
            "list_tags",
            "search_tags",
        ):
            assert getattr(AdminNotesApiController, handler_name).cache is False

    def test_competency_matrix_get_handlers_use_matrix_cache(self) -> None:
        for handler_name in (
            "list_competency_matrix_sheet",
            "list_competency_matrix_items",
            "get_competency_matrix_item",
            "get_public_competency_matrix_item",
        ):
            handler = getattr(PublicCompetencyMatrixApiController, handler_name)

            assert handler.cache == settings.app.get_cache_duration(
                constants.response_cache.default_ttl_seconds,
            )
            assert handler.cache_key_builder is not None
            assert handler.cache_key_builder(cast("Any", FakeRequest())).startswith(
                "competency_matrix:",
            )

    def test_admin_competency_matrix_get_handlers_are_not_cached(self) -> None:
        for handler_name in (
            "list_competency_matrix_sheet",
            "search_competency_matrix_resources",
            "list_queued_competency_matrix_questions",
            "list_competency_matrix_items",
            "get_competency_matrix_item",
        ):
            assert getattr(AdminCompetencyMatrixApiController, handler_name).cache is False

    def test_i18n_get_handlers_use_i18n_cache(self) -> None:
        for handler_name in ("list_languages", "get_bundle"):
            handler = getattr(I18nApiController, handler_name)

            assert handler.cache == settings.app.get_cache_duration(
                constants.response_cache.default_ttl_seconds,
            )
            assert handler.cache_key_builder is not None
            assert handler.cache_key_builder(cast("Any", FakeRequest())).startswith("i18n:")

    def test_healthcheck_uses_domain_cache_key(self) -> None:
        handler = HealthcheckController.health

        assert handler.cache == settings.app.get_cache_duration(1)
        assert handler.cache_key_builder is not None
        assert handler.cache_key_builder(cast("Any", FakeRequest())).startswith("healthcheck:")


class TestResponseCacheCli:
    def test_registers_invalidate_cache_command(self) -> None:
        cli = click.Group()

        CLIPlugin().on_cli_init(cli)

        assert "invalidatecache" in cli.commands
        assert "createsuperuser" in cli.commands
        assert "initbuckets" in cli.commands
