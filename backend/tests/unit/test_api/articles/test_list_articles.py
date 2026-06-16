import uuid
from datetime import date
from typing import cast

import pytest_asyncio
from httpx import codes
from litestar.di import Provide

from core.articles.schemas import ArticleFilters, ArticlePublicStatsCollection
from core.auth.enums import RoleEnum
from core.auth.exceptions import UnauthorizedError
from core.auth.schemas import JwtUser
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from entrypoints.litestar.api.articles.dependencies import (
    provide_article_filters,
    provide_public_article_filters,
)
from entrypoints.litestar.api.articles.endpoints import (
    AdminArticlesApiController,
    PublicArticlesApiController,
)
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestListArticlesAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.authentication_use_case = await self.container.get_auth_use_case()
        self.use_case = await self.container.get_articles_use_case()
        self.analytics_use_case = await self.container.get_article_analytics_use_case()
        self.analytics_use_case.get_public_stats.return_value = ArticlePublicStatsCollection(
            values=[],
        )

    def test_list_articles_uses_litestar_dependency_for_filters(self) -> None:
        handler = PublicArticlesApiController.list_articles
        dependencies = handler.dependencies

        assert dependencies is not None
        assert "filters" in dependencies
        provider = cast("Provide", dependencies["filters"])
        assert provider.dependency is provide_public_article_filters
        assert provider.sync_to_thread is False

    def test_admin_list_articles_uses_litestar_dependency_for_filters(self) -> None:
        handler = AdminArticlesApiController.list_articles
        dependencies = handler.dependencies

        assert dependencies is not None
        assert "filters" in dependencies
        provider = cast("Provide", dependencies["filters"])
        assert provider.dependency is provide_article_filters
        assert provider.sync_to_thread is False

    def test_provide_article_filters_builds_filters_from_query_parameters(self) -> None:
        filters = provide_article_filters(
            page=2,
            page_size=5,
            only_published=True,
            language=LanguageEnum.RU,
            tag_slug="python",
            published_from=date(2026, 1, 1),
            published_to=date(2026, 1, 31),
            search_query="  typed articles  ",
        )

        assert filters == ArticleFilters(
            page=2,
            page_size=5,
            language=LanguageEnum.RU,
            only_published=True,
            tag_slug="python",
            published_from=date(2026, 1, 1),
            published_to=date(2026, 1, 31),
            search_query="typed articles",
            include_tags=True,
        )

    def test_provide_public_article_filters_builds_published_filters(self) -> None:
        filters = provide_public_article_filters(
            page=2,
            page_size=5,
            language=LanguageEnum.RU,
            tag_slug="python",
            published_from=date(2026, 1, 1),
            published_to=date(2026, 1, 31),
            search_query="  typed articles  ",
        )

        assert filters == ArticleFilters(
            page=2,
            page_size=5,
            language=LanguageEnum.RU,
            only_published=True,
            tag_slug="python",
            published_from=date(2026, 1, 1),
            published_to=date(2026, 1, 31),
            search_query="typed articles",
            include_tags=True,
        )

    def test_provide_article_filters_normalizes_blank_search_query(self) -> None:
        filters = provide_article_filters(
            page=1,
            page_size=10,
            only_published=True,
            language=LanguageEnum.RU,
            tag_slug=None,
            published_from=None,
            published_to=None,
            search_query="   ",
        )

        assert filters.search_query is None

    def test_list_articles(self) -> None:
        tag = self.factory.core.tag(tag_id=1, name="Python", slug="python")
        article = self.factory.core.article(
            article_id=uuid.UUID(int=1),
            title="Typed articles",
            content="Typed articles content for excerpt.",
            slug="typed-articles",
            folder="Engineering",
            author_username="admin",
            publish_status=PublishStatusEnum.PUBLISHED,
            published_at="2026-01-02T03:04:05",
            created_at="2026-01-01T03:04:05",
            updated_at="2026-01-03T03:04:05",
            tags=[tag],
        )
        self.use_case.list_articles.return_value = self.factory.core.article_list(
            articles=[article],
            total_count=1,
            total_pages=1,
        )

        response = self.api.get_articles(page=1, page_size=10, tag_slug="python")

        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "totalCount": 1,
            "totalPages": 1,
            "articles": [
                {
                    "id": str(article.id),
                    "title": "Typed articles",
                    "slug": "typed-articles",
                    "folder": "Engineering",
                    "authorUsername": "admin",
                    "publishedAt": "2026-01-02T03:04:05+00:00",
                    "publishStatus": "Published",
                    "updatedAt": "2026-01-03T03:04:05+00:00",
                    "excerpt": "Typed articles content for excerpt.",
                    "metadata": {
                        "seoTitleRu": None,
                        "seoTitleEn": None,
                        "seoDescriptionRu": None,
                        "seoDescriptionEn": None,
                        "coverImageUrl": None,
                        "coverImageAltRu": None,
                        "coverImageAltEn": None,
                    },
                    "tags": [
                        {
                            "id": 1,
                            "name": "Python",
                            "slug": "python",
                            "deletedAt": None,
                            "translations": {
                                "ru": {"name": "Python"},
                                "en": {"name": "Python"},
                            },
                        },
                    ],
                },
            ],
        }
        self.use_case.list_articles.assert_called_once_with(
            filters=ArticleFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug="python",
                published_from=None,
                published_to=None,
                search_query=None,
                include_tags=True,
            ),
        )
        self.analytics_use_case.get_public_stats.assert_not_called()

    def test_list_articles_with_publish_date_range_and_search_query(self) -> None:
        self.use_case.list_articles.return_value = self.factory.core.article_list(
            articles=[],
            total_count=0,
            total_pages=0,
        )

        response = self.api.get_articles(
            page=2,
            page_size=5,
            published_from="2026-01-01",
            published_to="2026-01-31",
            search_query="  typed articles  ",
        )

        assert response.status_code == codes.OK, response.content
        self.use_case.list_articles.assert_called_once_with(
            filters=ArticleFilters(
                page=2,
                page_size=5,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug=None,
                published_from=date(2026, 1, 1),
                published_to=date(2026, 1, 31),
                search_query="typed articles",
                include_tags=True,
            ),
        )

    def test_list_articles_requires_explicit_page(self) -> None:
        response = self.api.get_articles(page=None, page_size=10)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.list_articles.assert_not_called()

    def test_list_articles_requires_explicit_language(self) -> None:
        response = self.api.get_articles(page=1, page_size=10, language=None)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.list_articles.assert_not_called()

    def test_anonymous_cannot_request_admin_articles(self) -> None:
        response = self.no_auth_api.get_admin_articles(page=1, page_size=10, only_published=False)

        assert response.status_code == codes.UNAUTHORIZED
        assert response.json()["message"] == UnauthorizedError.message
        self.use_case.list_articles.assert_not_called()

    def test_moderator_can_request_all_articles_from_admin_api(self) -> None:
        self.authentication_use_case.authenticate.return_value = JwtUser(
            username="moderator",
            role=RoleEnum.MODERATOR,
        )
        self.use_case.list_articles.return_value = self.factory.core.article_list(
            articles=[],
            total_count=0,
            total_pages=0,
        )

        response = self.api.get_admin_articles(page=1, page_size=10, only_published=False)

        assert response.status_code == codes.OK, response.content
        self.use_case.list_articles.assert_called_once_with(
            filters=ArticleFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=False,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query=None,
                include_tags=True,
            ),
        )
