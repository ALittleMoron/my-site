from datetime import date

import pytest_asyncio
from httpx import codes

from core.articles.schemas import ArticleFilters
from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser
from core.i18n.enums import LanguageEnum
from entrypoints.litestar.api.articles.endpoints import (
    AdminArticlesApiController,
    PublicArticlesApiController,
)
from entrypoints.litestar.api.competency_matrix.endpoints import (
    AdminCompetencyMatrixApiController,
    PublicCompetencyMatrixApiController,
)
from entrypoints.litestar.api.files.endpoints import FilesApiController
from entrypoints.litestar.api.resumes.endpoints import AdminResumesApiController
from entrypoints.litestar.api.routers import api_router
from entrypoints.litestar.api.wiki_links.endpoints import WikiLinksApiController
from entrypoints.litestar.guards import content_manager_guard, team_manager_guard
from tests.test_cases import ApiTestCase


class TestApiScopeRoutes(ApiTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.authentication_use_case = await self.container.get_auth_use_case()
        self.articles_use_case = await self.container.get_articles_use_case()

    def test_public_articles_list_forces_public_visibility(self) -> None:
        self.articles_use_case.list_articles.return_value = self.factory.core.article_list(
            articles=[],
            total_count=0,
            total_pages=0,
        )

        response = self.no_auth_api.client.get(
            "/api/articles",
            params={
                "page": 1,
                "pageSize": 10,
                "language": "ru",
                "onlyPublished": "false",
            },
        )

        assert response.status_code == codes.OK, response.content
        self.articles_use_case.list_articles.assert_called_once_with(
            filters=ArticleFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query=None,
                include_tags=True,
            ),
        )

    def test_admin_articles_list_uses_admin_prefix_for_draft_visibility(self) -> None:
        self.authentication_use_case.authenticate.return_value = JwtUser(
            username="moderator",
            role=RoleEnum.MODERATOR,
        )
        self.articles_use_case.list_articles.return_value = self.factory.core.article_list(
            articles=[],
            total_count=0,
            total_pages=0,
        )

        response = self.api.client.get(
            "/api/admin/articles",
            params={
                "page": 2,
                "pageSize": 5,
                "language": "en",
                "onlyPublished": "false",
                "publishedFrom": "2026-01-01",
                "publishedTo": "2026-01-31",
                "searchQuery": "  typed articles  ",
            },
        )

        assert response.status_code == codes.OK, response.content
        self.articles_use_case.list_articles.assert_called_once_with(
            filters=ArticleFilters(
                page=2,
                page_size=5,
                language=LanguageEnum.EN,
                only_published=False,
                tag_slug=None,
                published_from=date(2026, 1, 1),
                published_to=date(2026, 1, 31),
                search_query="typed articles",
                include_tags=True,
            ),
        )


class TestApiScopeRouteMetadata:
    def test_swagger_tags_are_scope_explicit_for_split_controllers(self) -> None:
        assert PublicArticlesApiController.tags == ["public articles"]
        assert AdminArticlesApiController.tags == ["admin articles"]
        assert PublicCompetencyMatrixApiController.tags == ["public competency matrix"]
        assert AdminCompetencyMatrixApiController.tags == ["admin competency matrix"]
        assert FilesApiController.tags == ["admin files"]
        assert AdminResumesApiController.tags == ["admin resumes"]
        assert WikiLinksApiController.tags == ["admin wiki links"]

    def test_operation_names_are_scope_explicit_for_split_controllers(self) -> None:
        assert PublicArticlesApiController.list_articles.name == "public-articles-list-api-handler"
        assert AdminArticlesApiController.list_articles.name == "admin-articles-list-api-handler"
        assert (
            PublicCompetencyMatrixApiController.suggest_competency_matrix_question.name
            == "public-competency-matrix-question-suggestion-create-api-handler"
        )
        assert (
            PublicCompetencyMatrixApiController.list_competency_matrix_items.name
            == "public-competency-matrix-items-list-api-handler"
        )
        assert (
            AdminCompetencyMatrixApiController.list_competency_matrix_items.name
            == "admin-competency-matrix-items-list-api-handler"
        )
        assert (
            AdminCompetencyMatrixApiController.list_queued_competency_matrix_questions.name
            == "admin-competency-matrix-queued-questions-list-api-handler"
        )
        assert (
            AdminCompetencyMatrixApiController.create_queued_competency_matrix_question.name
            == "admin-competency-matrix-queued-question-create-api-handler"
        )
        assert (
            AdminCompetencyMatrixApiController.import_queued_competency_matrix_questions.name
            == "admin-competency-matrix-queued-questions-import-api-handler"
        )
        assert (
            AdminCompetencyMatrixApiController.delete_queued_competency_matrix_question.name
            == "admin-competency-matrix-queued-question-delete-api-handler"
        )
        assert (
            AdminCompetencyMatrixApiController.create_competency_matrix_item_from_queue.name
            == "admin-competency-matrix-queued-question-create-item-api-handler"
        )
        assert FilesApiController.upload_file.name == "admin-files-upload-api-handler"
        assert FilesApiController.list_files.name == "admin-files-list-api-handler"
        assert FilesApiController.get_file.name == "admin-files-detail-api-handler"
        assert FilesApiController.update_file.name == "admin-files-update-api-handler"
        assert FilesApiController.delete_file.name == "admin-files-delete-api-handler"
        assert AdminResumesApiController.list_resumes.name == "admin-resumes-list-api-handler"
        assert AdminResumesApiController.create_resume.name == "admin-resumes-create-api-handler"
        assert AdminResumesApiController.get_resume.name == "admin-resumes-detail-api-handler"
        assert AdminResumesApiController.update_resume.name == "admin-resumes-update-api-handler"
        assert AdminResumesApiController.delete_resume.name == "admin-resumes-delete-api-handler"
        assert AdminResumesApiController.export_resume.name == "admin-resumes-export-api-handler"
        assert (
            WikiLinksApiController.list_wiki_link_targets.name
            == "admin-wiki-links-targets-list-api-handler"
        )

    def test_resumes_admin_urls_are_not_exposed_under_public_api(self) -> None:
        route_paths = _api_route_paths()

        assert AdminResumesApiController.guards == [team_manager_guard]
        assert "/api/resumes" not in route_paths
        assert "/api/resumes/{resume_id:str}" not in route_paths
        assert "/api/resumes/{resume_id:str}/export" not in route_paths
        assert "/api/admin/resumes" in route_paths
        assert "/api/admin/resumes/{resume_id:str}" in route_paths
        assert "/api/admin/resumes/{resume_id:str}/export" in route_paths

    def test_matrix_admin_urls_are_not_exposed_under_public_api(self) -> None:
        route_paths = _api_route_paths()

        assert AdminCompetencyMatrixApiController.guards == [content_manager_guard]
        assert "/api/competency-matrix/resources/search" not in route_paths
        assert "/api/competency-matrix/queued-questions" not in route_paths
        assert "/api/competency-matrix/queued-questions/import" not in route_paths
        assert "/api/admin/competency-matrix/resources/search" in route_paths
        assert "/api/admin/competency-matrix/queued-questions" in route_paths
        assert "/api/admin/competency-matrix/queued-questions/import" in route_paths


def _api_route_paths() -> set[str]:
    return {route.path for route in api_router.routes}
