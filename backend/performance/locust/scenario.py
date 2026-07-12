from secrets import choice

from core.i18n.enums import LanguageEnum
from entrypoints.litestar.api.articles.schemas import (
    ArticleDetailResponseSchema,
    ArticleListResponseSchema,
    ArticleTreeResponseSchema,
)
from entrypoints.litestar.api.competency_matrix.schemas import (
    CompetencyMatrixSheetsListResponseSchema,
    PublicCompetencyMatrixItemDetailResponseSchema,
    PublicCompetencyMatrixItemsListResponseSchema,
)
from entrypoints.litestar.api.i18n.schemas import (
    I18nBundleResponseSchema,
    LanguagesResponseSchema,
)
from performance.locust import constants
from performance.locust.http import LocustHttpClient, PerformanceApiClient
from performance.locust.settings import LocustScenarioSettings


class PublicSiteDiscovery:
    def __init__(
        self,
        *,
        api_client: PerformanceApiClient,
        language: LanguageEnum,
        matrix_sheet_key_prefix: str | None,
    ) -> None:
        self.api_client = api_client
        self.language = language
        self.matrix_sheet_key_prefix = matrix_sheet_key_prefix

    def discover_matrix_sheets(self) -> list[str]:
        schema = self.api_client.get_validated(
            f"/api/competency-matrix/sheets?language={self.language.value}",
            name="GET /api/competency-matrix/sheets",
            schema_type=CompetencyMatrixSheetsListResponseSchema,
        )
        if schema is None:
            return []
        return [
            sheet.key
            for sheet in schema.sheets
            if self.matrix_sheet_key_prefix is None
            or sheet.key.startswith(self.matrix_sheet_key_prefix)
        ]

    def discover_article_slugs(self) -> list[str]:
        schema = self.api_client.get_validated(
            "/api/articles"
            f"?page=1&pageSize={constants.DISCOVERY_ARTICLES_PAGE_SIZE}"
            f"&language={self.language.value}",
            name="GET /api/articles",
            schema_type=ArticleListResponseSchema,
        )
        if schema is None:
            return []
        return [article.slug for article in schema.articles]

    def discover_matrix_item_slugs(self, *, matrix_sheets: list[str]) -> list[str]:
        slugs: list[str] = []
        for sheet_key in matrix_sheets:
            schema = self.api_client.get_validated(
                f"/api/competency-matrix/items?sheetKey={sheet_key}&language={self.language.value}",
                name="GET /api/competency-matrix/items",
                schema_type=PublicCompetencyMatrixItemsListResponseSchema,
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
    def __init__(self, *, client: LocustHttpClient, settings: LocustScenarioSettings) -> None:
        self.language = settings.language
        self.include_spa = settings.include_spa
        self.include_matrix_suggestions = settings.include_matrix_suggestions
        self.matrix_suggestion_number = 0
        self.api_client = PerformanceApiClient(
            client=client,
            validate_responses=settings.validate_responses,
        )
        self.discovery = PublicSiteDiscovery(
            api_client=self.api_client,
            language=self.language,
            matrix_sheet_key_prefix=(
                constants.SEEDED_ENTITY_PREFIX if settings.seed_data else None
            ),
        )
        self.matrix_sheets = self.discovery.discover_matrix_sheets()
        self.article_slugs = self.discovery.discover_article_slugs()
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

    def articles_list(self) -> None:
        self.api_client.get(
            "/api/articles"
            f"?page=1&pageSize={constants.ARTICLES_LIST_PAGE_SIZE}"
            f"&language={self.language.value}",
            name="GET /api/articles",
            schema_type=ArticleListResponseSchema,
        )

    def articles_tree(self) -> None:
        self.api_client.get(
            f"/api/articles/tree?language={self.language.value}",
            name="GET /api/articles/tree",
            schema_type=ArticleTreeResponseSchema,
        )

    def article_detail(self) -> None:
        if not self.article_slugs:
            self.article_slugs = self.discovery.discover_article_slugs()
            return
        self.api_client.get(
            f"/api/articles/detail/{choice(self.article_slugs)}?language={self.language.value}",
            name="GET /api/articles/detail/:slug",
            schema_type=ArticleDetailResponseSchema,
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
            f"&language={self.language.value}",
            name="GET /api/competency-matrix/items",
            schema_type=PublicCompetencyMatrixItemsListResponseSchema,
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
            schema_type=PublicCompetencyMatrixItemDetailResponseSchema,
        )

    def matrix_question_suggestion(self) -> None:
        if not self.include_matrix_suggestions or not self.matrix_sheets:
            return
        self.matrix_suggestion_number += 1
        with self.api_client.client.post(
            "/api/competency-matrix/question-suggestions",
            name="POST /api/competency-matrix/question-suggestions",
            json={
                "question": (
                    f"{constants.MATRIX_QUESTION_SUGGESTION_PREFIX} "
                    f"{self.language.value}-{self.matrix_suggestion_number}"
                ),
                "sheet": choice(self.matrix_sheets),
            },
            catch_response=True,
        ) as response:
            if response.status_code in constants.MATRIX_QUESTION_SUGGESTION_SUCCESS_STATUSES:
                return
            response.failure(
                f"POST /api/competency-matrix/question-suggestions returned {response.status_code}",
            )

    def spa_root(self) -> None:
        if self.include_spa:
            self.api_client.client.get("/", name="GET /")
