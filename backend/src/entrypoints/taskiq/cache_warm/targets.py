from collections.abc import Iterable
from dataclasses import dataclass

from pydantic import BaseModel

from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItemBySlugGetParams,
    CompetencyMatrixItemFilters,
    CompetencyMatrixItemGetParams,
    CompetencyMatrixItems,
    Sheets,
)
from core.competency_matrix.use_cases import AbstractCompetencyMatrixUseCase
from core.i18n.enums import LanguageEnum
from core.notes.schemas import Note, NoteFilters, Notes, NoteTree, Tags
from core.notes.use_cases import AbstractNotesUseCase
from entrypoints.litestar.api.competency_matrix.schemas import (
    CompetencyMatrixItemDetailResponseSchema,
    CompetencyMatrixItemsListResponseSchema,
    CompetencyMatrixSheetsListResponseSchema,
)
from entrypoints.litestar.api.i18n.catalog import get_i18n_messages, get_language_label
from entrypoints.litestar.api.i18n.schemas import (
    I18nBundleResponseSchema,
    LanguageResponseSchema,
    LanguagesResponseSchema,
)
from entrypoints.litestar.api.notes.schemas import (
    NoteDetailResponseSchema,
    NoteListResponseSchema,
    NoteTreeResponseSchema,
    TagsResponseSchema,
)
from entrypoints.litestar.response_cache import ResponseCacheDomain
from infra.config.settings import settings


@dataclass(frozen=True, slots=True)
class CacheWarmTarget:
    domain: ResponseCacheDomain
    path: str
    query: tuple[tuple[str, str], ...]
    response: BaseModel


@dataclass(frozen=True, slots=True)
class CacheWarmQueryBuilder:
    def build(self, *values: tuple[str, str]) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(values, key=lambda item: item[0]))


@dataclass(frozen=True, slots=True)
class I18nCacheWarmTargetCollector:
    def collect(self) -> list[CacheWarmTarget]:
        return [
            self._languages_target(),
            *[self._bundle_target(language=language) for language in LanguageEnum],
        ]

    def _languages_target(self) -> CacheWarmTarget:
        return CacheWarmTarget(
            domain=ResponseCacheDomain.I18N,
            path="/api/i18n/languages",
            query=(),
            response=LanguagesResponseSchema(
                default_language=settings.i18n.default_language,
                languages=[
                    LanguageResponseSchema.from_language(
                        language=language,
                        label=get_language_label(language=language),
                    )
                    for language in LanguageEnum
                ],
            ),
        )

    def _bundle_target(self, *, language: LanguageEnum) -> CacheWarmTarget:
        return CacheWarmTarget(
            domain=ResponseCacheDomain.I18N,
            path=f"/api/i18n/bundles/{language.value}",
            query=(),
            response=I18nBundleResponseSchema(
                language=language,
                messages=dict(get_i18n_messages(language=language)),
            ),
        )


@dataclass(frozen=True, slots=True)
class NotesCacheWarmTargetCollector:
    notes_use_case: AbstractNotesUseCase
    query_builder: CacheWarmQueryBuilder

    async def collect(self) -> list[CacheWarmTarget]:
        targets: list[CacheWarmTarget] = []
        for language in LanguageEnum:
            targets.extend(await self._collect_language_targets(language=language))
        return targets

    async def _collect_language_targets(self, *, language: LanguageEnum) -> list[CacheWarmTarget]:
        tags = await self.notes_use_case.list_tags(include_deleted=False, language=language)
        tree = await self.notes_use_case.list_tree(only_published=True, language=language)
        notes = await self.notes_use_case.list_notes(
            filters=self._build_list_filters(language=language),
        )
        return [
            self._tags_target(tags=tags, language=language),
            self._tree_target(tree=tree, language=language),
            self._list_target(notes=notes, language=language),
            *await self._detail_targets(notes=notes, language=language),
        ]

    def _build_list_filters(self, *, language: LanguageEnum) -> NoteFilters:
        return NoteFilters(
            page=1,
            page_size=settings.cache_warm.notes_page_size,
            language=language,
            only_published=True,
            tag_slug=None,
            published_from=None,
            published_to=None,
            search_query=None,
            include_tags=True,
            order_for_seo=False,
        )

    def _tags_target(self, *, tags: Tags, language: LanguageEnum) -> CacheWarmTarget:
        return CacheWarmTarget(
            domain=ResponseCacheDomain.NOTES,
            path="/api/notes/tags",
            query=self.query_builder.build(("language", language.value)),
            response=TagsResponseSchema.from_domain_schema(
                schema=tags,
                language=language,
            ),
        )

    def _tree_target(self, *, tree: NoteTree, language: LanguageEnum) -> CacheWarmTarget:
        return CacheWarmTarget(
            domain=ResponseCacheDomain.NOTES,
            path="/api/notes/tree",
            query=self.query_builder.build(("language", language.value)),
            response=NoteTreeResponseSchema.from_domain_schema(schema=tree),
        )

    def _list_target(self, *, notes: Notes, language: LanguageEnum) -> CacheWarmTarget:
        return CacheWarmTarget(
            domain=ResponseCacheDomain.NOTES,
            path="/api/notes",
            query=self.query_builder.build(
                ("language", language.value),
                ("page", "1"),
                ("pageSize", str(settings.cache_warm.notes_page_size)),
            ),
            response=NoteListResponseSchema.from_domain_schema(
                schema=notes,
                language=language,
            ),
        )

    async def _detail_targets(
        self,
        *,
        notes: Notes,
        language: LanguageEnum,
    ) -> list[CacheWarmTarget]:
        return [
            self._detail_target(
                note=note,
                detail=await self._load_detail(note=note),
                language=language,
            )
            for note in notes.values
        ]

    async def _load_detail(self, *, note: Note) -> Note:
        return await self.notes_use_case.get_note(slug=note.slug, only_published=True)

    def _detail_target(
        self,
        *,
        note: Note,
        detail: Note,
        language: LanguageEnum,
    ) -> CacheWarmTarget:
        return CacheWarmTarget(
            domain=ResponseCacheDomain.NOTES,
            path=f"/api/notes/detail/{note.slug}",
            query=self.query_builder.build(("language", language.value)),
            response=NoteDetailResponseSchema.from_domain_schema(
                schema=detail,
                language=language,
            ),
        )


@dataclass(frozen=True, slots=True)
class CompetencyMatrixCacheWarmTargetCollector:
    matrix_use_case: AbstractCompetencyMatrixUseCase
    query_builder: CacheWarmQueryBuilder

    async def collect(self) -> list[CacheWarmTarget]:
        targets: list[CacheWarmTarget] = []
        for language in LanguageEnum:
            targets.extend(await self._collect_language_targets(language=language))
        return targets

    async def _collect_language_targets(self, *, language: LanguageEnum) -> list[CacheWarmTarget]:
        sheets = await self.matrix_use_case.list_sheets()
        return [
            self._sheets_target(sheets=sheets, language=language),
            *await self._sheet_item_targets(sheets=sheets, language=language),
        ]

    def _sheets_target(self, *, sheets: Sheets, language: LanguageEnum) -> CacheWarmTarget:
        return CacheWarmTarget(
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
            path="/api/competency-matrix/sheets",
            query=self.query_builder.build(("language", language.value)),
            response=CompetencyMatrixSheetsListResponseSchema.from_domain_schema(
                schema=sheets,
                language=language,
            ),
        )

    async def _sheet_item_targets(
        self,
        *,
        sheets: Sheets,
        language: LanguageEnum,
    ) -> list[CacheWarmTarget]:
        targets: list[CacheWarmTarget] = []
        for sheet in sheets:
            items = await self.matrix_use_case.list_items(
                filters=CompetencyMatrixItemFilters(
                    sheet_key=sheet.key,
                    only_published=True,
                ),
            )
            targets.append(
                self._items_target(sheet_key=sheet.key, items=items, language=language),
            )
            targets.extend(await self._item_detail_targets(items=items, language=language))
        return targets

    def _items_target(
        self,
        *,
        sheet_key: str,
        items: CompetencyMatrixItems,
        language: LanguageEnum,
    ) -> CacheWarmTarget:
        return CacheWarmTarget(
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
            path="/api/competency-matrix/items",
            query=self.query_builder.build(
                ("language", language.value),
                ("sheetKey", sheet_key),
            ),
            response=CompetencyMatrixItemsListResponseSchema.from_domain_schema(
                sheet_key=sheet_key,
                schema=items,
                language=language,
            ),
        )

    async def _item_detail_targets(
        self,
        *,
        items: CompetencyMatrixItems,
        language: LanguageEnum,
    ) -> list[CacheWarmTarget]:
        targets: list[CacheWarmTarget] = []
        for item in items.values:
            targets.extend(await self._single_item_detail_targets(item=item, language=language))
        return targets

    async def _single_item_detail_targets(
        self,
        *,
        item: CompetencyMatrixItem,
        language: LanguageEnum,
    ) -> list[CacheWarmTarget]:
        detail = await self.matrix_use_case.get_item(
            params=CompetencyMatrixItemGetParams(
                item_id=item.id,
                only_published=True,
            ),
        )
        public_detail = await self.matrix_use_case.get_item_by_slug(
            params=CompetencyMatrixItemBySlugGetParams(
                slug=item.slug,
                only_published=True,
            ),
        )
        return [
            self._public_detail_target(item=item, detail=public_detail, language=language),
            self._admin_detail_target(item=item, detail=detail, language=language),
        ]

    def _public_detail_target(
        self,
        *,
        item: CompetencyMatrixItem,
        detail: CompetencyMatrixItem,
        language: LanguageEnum,
    ) -> CacheWarmTarget:
        return CacheWarmTarget(
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
            path=f"/api/competency-matrix/items/public/{item.slug}",
            query=self.query_builder.build(("language", language.value)),
            response=CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
                schema=detail,
                language=language,
            ),
        )

    def _admin_detail_target(
        self,
        *,
        item: CompetencyMatrixItem,
        detail: CompetencyMatrixItem,
        language: LanguageEnum,
    ) -> CacheWarmTarget:
        return CacheWarmTarget(
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
            path=f"/api/competency-matrix/items/detail/{int(item.id)}",
            query=self.query_builder.build(("language", language.value)),
            response=CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
                schema=detail,
                language=language,
            ),
        )


@dataclass(frozen=True, slots=True)
class ResponseCacheWarmTargetCollector:
    i18n_collector: I18nCacheWarmTargetCollector
    notes_collector: NotesCacheWarmTargetCollector
    matrix_collector: CompetencyMatrixCacheWarmTargetCollector

    async def collect(self, *, domains: Iterable[ResponseCacheDomain]) -> list[CacheWarmTarget]:
        requested_domains = tuple(domains)
        targets: list[CacheWarmTarget] = []
        if ResponseCacheDomain.I18N in requested_domains:
            targets.extend(self.i18n_collector.collect())
        if ResponseCacheDomain.NOTES in requested_domains:
            targets.extend(await self.notes_collector.collect())
        if ResponseCacheDomain.COMPETENCY_MATRIX in requested_domains:
            targets.extend(await self.matrix_collector.collect())
        return targets
