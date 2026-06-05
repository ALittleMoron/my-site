from collections.abc import Mapping
from secrets import choice

from core.i18n.enums import LanguageEnum
from entrypoints.litestar.api.competency_matrix.schemas import (
    CompetencyMatrixItemDetailResponseSchema,
    CompetencyMatrixItemsListResponseSchema,
    CompetencyMatrixResourcesResponseSchema,
    CompetencyMatrixSheetsListResponseSchema,
)
from entrypoints.litestar.api.i18n.schemas import (
    I18nBundleResponseSchema,
    LanguagesResponseSchema,
)
from entrypoints.litestar.api.notes.schemas import (
    NoteDetailResponseSchema,
    NoteListResponseSchema,
    NoteTreeResponseSchema,
)
from performance.locust.contracts import performance_language_from_environment
from performance.locust.http import LocustHttpClient, PerformanceApiClient


class PublicSiteDiscovery:
    def __init__(self, *, api_client: PerformanceApiClient, language: LanguageEnum) -> None:
        self.api_client = api_client
        self.language = language

    def discover_matrix_sheets(self) -> list[str]:
        schema = self.api_client.get_validated(
            f"/api/competency-matrix/sheets?language={self.language.value}",
            name="GET /api/competency-matrix/sheets",
            schema_type=CompetencyMatrixSheetsListResponseSchema,
        )
        if schema is None:
            return []
        return [sheet.key for sheet in schema.sheets]

    def discover_note_slugs(self) -> list[str]:
        schema = self.api_client.get_validated(
            f"/api/notes?page=1&pageSize=100&onlyPublished=true&language={self.language.value}",
            name="GET /api/notes",
            schema_type=NoteListResponseSchema,
        )
        if schema is None:
            return []
        return [note.slug for note in schema.notes]

    def discover_matrix_item_slugs(self, *, matrix_sheets: list[str]) -> list[str]:
        slugs: list[str] = []
        for sheet_key in matrix_sheets:
            schema = self.api_client.get_validated(
                "/api/competency-matrix/items"
                f"?sheetKey={sheet_key}"
                f"&onlyPublished=true&language={self.language.value}",
                name="GET /api/competency-matrix/items",
                schema_type=CompetencyMatrixItemsListResponseSchema,
            )
            if schema is None:
                continue
            slugs.extend(
                item.slug
                for section in schema.sections
                for subsection in section.subsections
                for grade in subsection.grades
                for item in grade.items
            )
        return slugs


class PublicSiteScenario:
    def __init__(self, *, client: LocustHttpClient, environ: Mapping[str, str]) -> None:
        self.language = performance_language_from_environment(environ)
        self.include_spa = environ["PERFORMANCE_INCLUDE_SPA"].lower() == "true"
        self.api_client = PerformanceApiClient(
            client=client,
            validate_responses=environ["PERFORMANCE_VALIDATE_RESPONSES"].lower() == "true",
        )
        self.discovery = PublicSiteDiscovery(
            api_client=self.api_client,
            language=self.language,
        )
        self.matrix_sheets = self.discovery.discover_matrix_sheets()
        self.note_slugs = self.discovery.discover_note_slugs()
        self.matrix_item_slugs = self.discovery.discover_matrix_item_slugs(
            matrix_sheets=self.matrix_sheets,
        )

    def healthcheck(self) -> None:
        self.api_client.client.get("/api/healthcheck", name="GET /api/healthcheck")

    def i18n_languages(self) -> None:
        self.api_client.get(
            "/api/i18n/languages",
            name="GET /api/i18n/languages",
            schema_type=LanguagesResponseSchema,
        )

    def i18n_bundle(self) -> None:
        self.api_client.get(
            f"/api/i18n/bundles/{self.language.value}",
            name="GET /api/i18n/bundles/:language",
            schema_type=I18nBundleResponseSchema,
        )

    def notes_list(self) -> None:
        self.api_client.get(
            f"/api/notes?page=1&pageSize=10&onlyPublished=true&language={self.language.value}",
            name="GET /api/notes",
            schema_type=NoteListResponseSchema,
        )

    def notes_tree(self) -> None:
        self.api_client.get(
            f"/api/notes/tree?language={self.language.value}",
            name="GET /api/notes/tree",
            schema_type=NoteTreeResponseSchema,
        )

    def note_detail(self) -> None:
        if not self.note_slugs:
            self.note_slugs = self.discovery.discover_note_slugs()
            return
        self.api_client.get(
            "/api/notes/detail/"
            f"{choice(self.note_slugs)}?onlyPublished=true&language={self.language.value}",
            name="GET /api/notes/detail/:slug",
            schema_type=NoteDetailResponseSchema,
        )

    def matrix_sheets_task(self) -> None:
        self.api_client.get(
            f"/api/competency-matrix/sheets?language={self.language.value}",
            name="GET /api/competency-matrix/sheets",
            schema_type=CompetencyMatrixSheetsListResponseSchema,
        )

    def matrix_items(self) -> None:
        if not self.matrix_sheets:
            self.matrix_sheets = self.discovery.discover_matrix_sheets()
            return
        self.api_client.get(
            "/api/competency-matrix/items"
            f"?sheetKey={choice(self.matrix_sheets)}"
            f"&onlyPublished=true&language={self.language.value}",
            name="GET /api/competency-matrix/items",
            schema_type=CompetencyMatrixItemsListResponseSchema,
        )

    def matrix_item_detail(self) -> None:
        if not self.matrix_item_slugs:
            if not self.matrix_sheets:
                self.matrix_sheets = self.discovery.discover_matrix_sheets()
            self.matrix_item_slugs = self.discovery.discover_matrix_item_slugs(
                matrix_sheets=self.matrix_sheets,
            )
            return
        self.api_client.get(
            "/api/competency-matrix/items/public/"
            f"{choice(self.matrix_item_slugs)}?language={self.language.value}",
            name="GET /api/competency-matrix/items/public/:slug",
            schema_type=CompetencyMatrixItemDetailResponseSchema,
        )

    def matrix_resources_search(self) -> None:
        self.api_client.get(
            "/api/competency-matrix/resources/search"
            f"?searchName=python&limit=5&language={self.language.value}",
            name="GET /api/competency-matrix/resources/search",
            schema_type=CompetencyMatrixResourcesResponseSchema,
        )

    def spa_root(self) -> None:
        if self.include_spa:
            self.api_client.client.get("/", name="GET /")
