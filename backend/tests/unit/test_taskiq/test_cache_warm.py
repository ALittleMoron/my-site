from dataclasses import dataclass, field
from datetime import timedelta
from typing import cast

import msgspec
import pytest
from litestar.stores.base import Store

from core.competency_matrix.schemas import (
    CompetencyMatrixItemBySlugGetParams,
    CompetencyMatrixItemFilters,
    CompetencyMatrixItemGetParams,
)
from core.competency_matrix.use_cases import AbstractCompetencyMatrixUseCase
from core.i18n.enums import LanguageEnum
from core.notes.schemas import NoteFilters, NoteTree
from core.notes.use_cases import AbstractNotesUseCase
from entrypoints.litestar.api.notes.schemas import NoteDetailResponseSchema
from entrypoints.litestar.response_cache import ResponseCacheDomain, ResponseCacheDomainStore
from entrypoints.taskiq.cache_warm.service import CacheWarmSummary, ResponseCacheWarmService
from entrypoints.taskiq.cache_warm.targets import (
    CacheWarmQueryBuilder,
    CacheWarmTarget,
    CompetencyMatrixCacheWarmTargetCollector,
    I18nCacheWarmTargetCollector,
    NotesCacheWarmTargetCollector,
    ResponseCacheWarmTargetCollector,
)
from entrypoints.taskiq.cache_warm.writer import (
    ResponseCacheKeyBuilder,
    ResponseCachePayloadCodec,
    ResponseCacheWarmWriter,
)
from infra.config.constants import constants
from infra.config.settings import settings
from tests.fixtures import FactoryFixture
from tests.helpers.factory import FactoryHelper


@dataclass
class FakeStore:
    values: dict[str, bytes] = field(default_factory=dict)
    set_calls: list[tuple[str, bytes | str, int | timedelta | None]] = field(default_factory=list)

    async def set(
        self,
        key: str,
        value: bytes | str,
        expires_in: int | timedelta | None = None,
    ) -> None:
        self.set_calls.append((key, value, expires_in))
        self.values[key] = value if isinstance(value, bytes) else value.encode()

    async def get(self, key: str, renew_for: int | timedelta | None = None) -> bytes | None:
        return self.values.get(key)

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)

    async def delete_all(self) -> None:
        self.values.clear()

    async def exists(self, key: str) -> bool:
        return key in self.values

    async def expires_in(self, key: str) -> int | None:
        return 60 if key in self.values else None


class FakeNotesUseCase:
    def __init__(self, factory: FactoryHelper) -> None:
        self.factory = factory
        self.list_notes_filters: list[NoteFilters] = []
        self.list_tree_languages: list[LanguageEnum] = []
        self.list_tags_languages: list[LanguageEnum] = []
        self.detail_slugs: list[str] = []
        self.notes = [
            factory.core.note(slug="first-note"),
            factory.core.note(slug="second-note"),
        ]

    async def list_notes(self, *, filters: NoteFilters):
        self.list_notes_filters.append(filters)
        return self.factory.core.note_list(notes=self.notes, total_count=2, total_pages=1)

    async def list_tree(self, *, only_published: bool, language: LanguageEnum):
        assert only_published is True
        self.list_tree_languages.append(language)
        return NoteTree(folders=[])

    async def list_tags(self, *, include_deleted: bool, language: LanguageEnum):
        assert include_deleted is False
        self.list_tags_languages.append(language)
        return self.factory.core.tags(values=[self.factory.core.tag(tag_id=1)])

    async def get_note(self, *, slug: str, only_published: bool):
        assert only_published is True
        self.detail_slugs.append(slug)
        return self.factory.core.note(slug=slug)


class FakeCompetencyMatrixUseCase:
    def __init__(self, factory: FactoryHelper) -> None:
        self.factory = factory
        self.list_items_filters: list[CompetencyMatrixItemFilters] = []
        self.detail_ids: list[int] = []
        self.public_detail_slugs: list[str] = []
        self.items = [
            factory.core.competency_matrix_item(
                item_id=1,
                slug="first-question",
                sheet_key="python",
                sheet="Python",
            ),
            factory.core.competency_matrix_item(
                item_id=2,
                slug="second-question",
                sheet_key="python",
                sheet="Python",
            ),
        ]

    async def list_sheets(self):
        return self.factory.core.sheets(values=["Python"])

    async def list_items(self, *, filters: CompetencyMatrixItemFilters):
        self.list_items_filters.append(filters)
        return self.factory.core.competency_matrix_items(values=self.items)

    async def get_item(self, *, params: CompetencyMatrixItemGetParams):
        assert params.only_published is True
        self.detail_ids.append(params.item_id)
        return self.items[int(params.item_id) - 1]

    async def get_item_by_slug(self, *, params: CompetencyMatrixItemBySlugGetParams):
        assert params.only_published is True
        self.public_detail_slugs.append(params.slug)
        return next(item for item in self.items if item.slug == params.slug)


class TestCacheWarmTargetGeneration(FactoryFixture):
    async def test_collects_canonical_targets_for_both_languages(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(settings.cache_warm, "notes_page_size", 10)
        notes_use_case = FakeNotesUseCase(factory=self.factory)
        matrix_use_case = FakeCompetencyMatrixUseCase(factory=self.factory)
        query_builder = CacheWarmQueryBuilder()
        collector = ResponseCacheWarmTargetCollector(
            i18n_collector=I18nCacheWarmTargetCollector(),
            notes_collector=NotesCacheWarmTargetCollector(
                notes_use_case=cast("AbstractNotesUseCase", notes_use_case),
                query_builder=query_builder,
            ),
            matrix_collector=CompetencyMatrixCacheWarmTargetCollector(
                matrix_use_case=cast("AbstractCompetencyMatrixUseCase", matrix_use_case),
                query_builder=query_builder,
            ),
        )

        targets = await collector.collect(
            domains=(
                ResponseCacheDomain.I18N,
                ResponseCacheDomain.NOTES,
                ResponseCacheDomain.COMPETENCY_MATRIX,
            ),
        )
        target_paths = {(target.domain, target.path, target.query) for target in targets}

        for language in LanguageEnum:
            assert (
                ResponseCacheDomain.I18N,
                f"/api/i18n/bundles/{language.value}",
                (),
            ) in target_paths
            assert (
                ResponseCacheDomain.NOTES,
                "/api/notes",
                (
                    ("language", language.value),
                    ("page", "1"),
                    ("pageSize", "10"),
                ),
            ) in target_paths
            assert (
                ResponseCacheDomain.NOTES,
                "/api/notes/tags",
                (("language", language.value),),
            ) in target_paths
            assert (
                ResponseCacheDomain.NOTES,
                "/api/notes/tree",
                (("language", language.value),),
            ) in target_paths
            assert (
                ResponseCacheDomain.COMPETENCY_MATRIX,
                "/api/competency-matrix/sheets",
                (("language", language.value),),
            ) in target_paths
            assert (
                ResponseCacheDomain.COMPETENCY_MATRIX,
                "/api/competency-matrix/items",
                (
                    ("language", language.value),
                    ("sheetKey", "python"),
                ),
            ) in target_paths

        assert (
            ResponseCacheDomain.I18N,
            "/api/i18n/languages",
            (),
        ) in target_paths
        assert notes_use_case.list_notes_filters == [
            NoteFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                include_tags=True,
            ),
            NoteFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.EN,
                only_published=True,
                include_tags=True,
            ),
        ]

    async def test_domain_specific_collection_limits_use_case_work(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(settings.cache_warm, "notes_page_size", 10)
        notes_use_case = FakeNotesUseCase(factory=self.factory)
        matrix_use_case = FakeCompetencyMatrixUseCase(factory=self.factory)
        query_builder = CacheWarmQueryBuilder()
        collector = ResponseCacheWarmTargetCollector(
            i18n_collector=I18nCacheWarmTargetCollector(),
            notes_collector=NotesCacheWarmTargetCollector(
                notes_use_case=cast("AbstractNotesUseCase", notes_use_case),
                query_builder=query_builder,
            ),
            matrix_collector=CompetencyMatrixCacheWarmTargetCollector(
                matrix_use_case=cast("AbstractCompetencyMatrixUseCase", matrix_use_case),
                query_builder=query_builder,
            ),
        )

        targets = await collector.collect(
            domains=(ResponseCacheDomain.NOTES,),
        )

        assert {target.domain for target in targets} == {ResponseCacheDomain.NOTES}
        assert notes_use_case.list_notes_filters
        assert matrix_use_case.list_items_filters == []


class TestCacheWarmWriter(FactoryFixture):
    async def test_writes_litestar_compatible_payload_to_domain_store(self) -> None:
        notes_store = FakeStore()
        store = ResponseCacheDomainStore(
            stores={ResponseCacheDomain.NOTES: cast("Store", notes_store)},
        )
        response = NoteDetailResponseSchema.from_domain_schema(
            schema=self.factory.core.note(slug="first-note"),
            language=LanguageEnum.EN,
        )
        target = CacheWarmTarget(
            domain=ResponseCacheDomain.NOTES,
            path="/api/notes/detail/first-note",
            query=(("language", "en"),),
            response=response,
        )
        key_builder = ResponseCacheKeyBuilder()
        payload_codec = ResponseCachePayloadCodec()

        await ResponseCacheWarmWriter(
            store=store,
            key_builder=key_builder,
            payload_codec=payload_codec,
        ).write_target(target)

        assert key_builder.build(target=target) == (
            "notes:GET/api/notes/detail/first-notelanguage=en"
        )
        assert notes_store.set_calls[0][0] == "GET/api/notes/detail/first-notelanguage=en"
        assert notes_store.set_calls[0][2] == constants.response_cache.default_ttl_seconds
        payload = notes_store.set_calls[0][1]
        assert isinstance(payload, bytes)
        messages = msgspec.msgpack.decode(payload)
        assert messages == [
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"application/json"]],
            },
            {
                "type": "http.response.body",
                "body": response.model_dump_json(by_alias=True).encode(),
            },
        ]

    async def test_cache_disabled_summary_skips_without_use_case_work(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(settings.app, "use_cache", False)
        notes_use_case = FakeNotesUseCase(factory=self.factory)
        matrix_use_case = FakeCompetencyMatrixUseCase(factory=self.factory)
        store = ResponseCacheDomainStore(stores={})
        query_builder = CacheWarmQueryBuilder()
        target_collector = ResponseCacheWarmTargetCollector(
            i18n_collector=I18nCacheWarmTargetCollector(),
            notes_collector=NotesCacheWarmTargetCollector(
                notes_use_case=cast("AbstractNotesUseCase", notes_use_case),
                query_builder=query_builder,
            ),
            matrix_collector=CompetencyMatrixCacheWarmTargetCollector(
                matrix_use_case=cast("AbstractCompetencyMatrixUseCase", matrix_use_case),
                query_builder=query_builder,
            ),
        )
        writer = ResponseCacheWarmWriter(
            store=store,
            key_builder=ResponseCacheKeyBuilder(),
            payload_codec=ResponseCachePayloadCodec(),
        )
        service = ResponseCacheWarmService(
            target_collector=target_collector,
            writer=writer,
            use_cache=False,
            supported_domains=(
                ResponseCacheDomain.I18N,
                ResponseCacheDomain.NOTES,
                ResponseCacheDomain.COMPETENCY_MATRIX,
            ),
        )

        summary = await service.warm_domains(
            domains=(ResponseCacheDomain.NOTES,),
        )

        assert summary == CacheWarmSummary(attempted=0, written=0, skipped=1)
        assert summary.as_dict() == {"attempted": 0, "written": 0, "skipped": 1}
        assert notes_use_case.list_notes_filters == []
        assert matrix_use_case.list_items_filters == []
