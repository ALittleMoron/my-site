import pytest
import pytest_asyncio
from httpx import codes

from core.articles.exceptions import ArticleNotFoundError
from core.articles.schemas import ArticleCreateParams, ArticleMetadata, ArticleUpdateParams
from core.enums import PublishStatusEnum
from entrypoints.litestar.response_cache import ResponseCacheDomain
from tests.test_cases import ApiTestCase


class TestAdminArticlesAPI(ApiTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.article_id = (await self.container.get_hex_uuid_id_generator()).get_next()
        self.use_case = await self.container.get_articles_use_case()

    def test_create_article_saves_author(self) -> None:
        article = self.factory.core.article(
            article_id=self.article_id,
            title="New article",
            content="New content",
            slug="new-article",
            folder="Inbox",
            author_username="test",
            publish_status=PublishStatusEnum.DRAFT,
            created_at="2026-01-01T03:04:05",
            updated_at="2026-01-01T03:04:05",
        )
        self.use_case.create_article.return_value = article

        response = self.api.post_create_article(
            data=self.factory.api.article_request(
                title_ru="Новая статья",
                title_en="New article",
                content_ru="Новое содержимое",
                content_en="New content",
                slug="new-article",
                folder_ru="Входящие",
                folder_en="Inbox",
                publish_status="Draft",
                tag_ids=[
                    "00000000000040008000000000000031",
                    "00000000000040008000000000000032",
                ],
            ),
        )

        assert response.status_code == codes.CREATED, response.content
        assert response.json()["authorUsername"] == "test"
        self.use_case.create_article.assert_called_once_with(
            params=ArticleCreateParams(
                id=self.article_id,
                slug="new-article",
                title_ru="Новая статья",
                title_en="New article",
                content_ru="Новое содержимое",
                content_en="New content",
                folder_ru="Входящие",
                folder_en="Inbox",
                author_username="test",
                publish_status=PublishStatusEnum.DRAFT,
                metadata=ArticleMetadata(
                    seo_title_ru="SEO статья",
                    seo_title_en="SEO article",
                    seo_description_ru="Описание для выдачи",
                    seo_description_en="Search result description",
                    cover_image_url="https://example.com/cover.jpg",
                    cover_image_alt_ru="Обложка статьи",
                    cover_image_alt_en="Article cover",
                ),
                tag_ids=[
                    "00000000000040008000000000000031",
                    "00000000000040008000000000000032",
                ],
            ),
        )

    def test_update_article(self) -> None:
        article = self.factory.core.article(
            article_id="00000000000040008000000000000022",
            title="Updated article",
            content="Updated content",
            slug="updated-article",
            folder="Inbox",
            author_username="test",
            publish_status=PublishStatusEnum.PUBLISHED,
            published_at="2026-01-02T03:04:05",
            created_at="2026-01-01T03:04:05",
            updated_at="2026-01-03T03:04:05",
        )
        self.use_case.update_article.return_value = article

        response = self.api.put_update_article(
            slug="old-article",
            data=self.factory.api.article_request(
                title_ru="Обновлённая статья",
                title_en="Updated article",
                content_ru="Обновлённое содержимое",
                content_en="Updated content",
                slug="updated-article",
                folder_ru="Входящие",
                folder_en="Inbox",
                publish_status="Published",
                metadata={
                    "seoTitleRu": "SEO обновлённая статья",
                    "seoTitleEn": "SEO updated article",
                    "seoDescriptionRu": "Обновлённое описание",
                    "seoDescriptionEn": "Updated description",
                    "coverImageUrl": None,
                    "coverImageAltRu": None,
                    "coverImageAltEn": None,
                },
                tag_ids=["00000000000040008000000000000031"],
            ),
        )

        assert response.status_code == codes.OK, response.content
        assert response.json()["slug"] == "updated-article"
        self.use_case.update_article.assert_called_once_with(
            slug="old-article",
            params=ArticleUpdateParams(
                slug="updated-article",
                title_ru="Обновлённая статья",
                title_en="Updated article",
                content_ru="Обновлённое содержимое",
                content_en="Updated content",
                folder_ru="Входящие",
                folder_en="Inbox",
                publish_status=PublishStatusEnum.PUBLISHED,
                metadata=ArticleMetadata(
                    seo_title_ru="SEO обновлённая статья",
                    seo_title_en="SEO updated article",
                    seo_description_ru="Обновлённое описание",
                    seo_description_en="Updated description",
                    cover_image_url=None,
                    cover_image_alt_ru=None,
                    cover_image_alt_en=None,
                ),
                tag_ids=["00000000000040008000000000000031"],
            ),
        )

    def test_create_article_requires_metadata_object(self) -> None:
        data = self.factory.api.article_request()
        del data["metadata"]

        response = self.api.post_create_article(data=data)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.create_article.assert_not_called()

    def test_create_article_allows_null_metadata_fields(self) -> None:
        self.use_case.create_article.return_value = self.factory.core.article(
            article_id=self.article_id,
            slug="nullable-metadata",
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        data = self.factory.api.article_request(
            slug="nullable-metadata",
            publish_status="Published",
            metadata={
                "seoTitleRu": None,
                "seoTitleEn": None,
                "seoDescriptionRu": None,
                "seoDescriptionEn": None,
                "coverImageUrl": None,
                "coverImageAltRu": None,
                "coverImageAltEn": None,
            },
        )

        response = self.api.post_create_article(data=data)

        assert response.status_code == codes.CREATED, response.content
        params = self.use_case.create_article.call_args.kwargs["params"]
        assert params.publish_status == PublishStatusEnum.PUBLISHED
        assert params.metadata == ArticleMetadata(
            seo_title_ru=None,
            seo_title_en=None,
            seo_description_ru=None,
            seo_description_en=None,
            cover_image_url=None,
            cover_image_alt_ru=None,
            cover_image_alt_en=None,
        )

    @pytest.mark.parametrize("slug", ["", "   ", "Invalid Slug", "invalid_slug", "-invalid"])
    def test_create_article_rejects_blank_or_invalid_slug(self, slug: str) -> None:
        response = self.api.post_create_article(data=self.factory.api.article_request(slug=slug))

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.create_article.assert_not_called()

    def test_create_article_rejects_whitespace_required_translation_fields(self) -> None:
        response = self.api.post_create_article(
            data=self.factory.api.article_request(title_ru="   ", folder_en="\t"),
        )

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.create_article.assert_not_called()

    def test_create_article_rejects_invalid_cover_url(self) -> None:
        data = self.factory.api.article_request()
        data["metadata"]["coverImageUrl"] = "ftp://example.com/cover.jpg"

        response = self.api.post_create_article(data=data)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.create_article.assert_not_called()

    def test_create_article_rejects_too_long_content(self) -> None:
        response = self.api.post_create_article(
            data=self.factory.api.article_request(content_en="x" * 100_001),
        )

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.create_article.assert_not_called()

    def test_create_article_requires_all_translation_fields(self) -> None:
        data = self.factory.api.article_request()
        del data["translations"]["en"]["content"]

        response = self.api.post_create_article(data=data)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.create_article.assert_not_called()

    def test_create_article_validation_error_does_not_enqueue_response_cache_warm(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        warmed_domains: list[ResponseCacheDomain] = []

        async def fake_invalidate_and_enqueue_response_cache_warm_domain(
            *,
            request: object,
            domain: ResponseCacheDomain,
        ) -> None:
            _ = request
            warmed_domains.append(domain)

        monkeypatch.setattr(
            "entrypoints.litestar.api.articles.endpoints.invalidate_and_enqueue_response_cache_warm_domain",
            fake_invalidate_and_enqueue_response_cache_warm_domain,
            raising=False,
        )
        data = self.factory.api.article_request()
        del data["translations"]["en"]["content"]

        response = self.api.post_create_article(data=data)

        assert response.status_code == codes.BAD_REQUEST
        assert warmed_domains == []

    def test_delete_article_not_found(self) -> None:
        self.use_case.delete_article.side_effect = ArticleNotFoundError()

        response = self.api.delete_article(slug="missing")

        assert response.status_code == codes.NOT_FOUND
        assert response.json()["message"] == ArticleNotFoundError.message

    def test_delete_article(self) -> None:
        response = self.api.delete_article(slug="old-article")

        assert response.status_code == codes.NO_CONTENT
        self.use_case.delete_article.assert_called_once_with(slug="old-article")

    def test_set_published_status_to_article(self) -> None:
        response = self.api.post_set_published_status_to_article(slug="draft-article")

        assert response.status_code == codes.NO_CONTENT
        self.use_case.switch_article_publish_status.assert_called_once_with(
            slug="draft-article",
            publish_status=PublishStatusEnum.PUBLISHED,
        )

    def test_set_draft_status_to_article(self) -> None:
        response = self.api.post_set_draft_status_to_article(slug="published-article")

        assert response.status_code == codes.NO_CONTENT
        self.use_case.switch_article_publish_status.assert_called_once_with(
            slug="published-article",
            publish_status=PublishStatusEnum.DRAFT,
        )

    def test_successful_article_mutations_enqueue_articles_response_cache_warm(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        warmed_domains: list[ResponseCacheDomain] = []

        async def fake_invalidate_and_enqueue_response_cache_warm_domain(
            *,
            request: object,
            domain: ResponseCacheDomain,
        ) -> None:
            _ = request
            warmed_domains.append(domain)

        monkeypatch.setattr(
            "entrypoints.litestar.api.articles.endpoints.invalidate_and_enqueue_response_cache_warm_domain",
            fake_invalidate_and_enqueue_response_cache_warm_domain,
            raising=False,
        )
        created_article = self.factory.core.article(
            article_id=self.article_id,
            slug="new-article",
            publish_status=PublishStatusEnum.DRAFT,
        )
        updated_article = self.factory.core.article(
            article_id="00000000000040008000000000000022",
            slug="updated-article",
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        self.use_case.create_article.return_value = created_article
        self.use_case.update_article.return_value = updated_article

        responses = [
            self.api.post_create_article(data=self.factory.api.article_request(slug="new-article")),
            self.api.put_update_article(
                slug="old-article",
                data=self.factory.api.article_request(slug="updated-article"),
            ),
            self.api.delete_article(slug="updated-article"),
            self.api.post_set_published_status_to_article(slug="draft-article"),
            self.api.post_set_draft_status_to_article(slug="published-article"),
        ]

        assert [response.status_code for response in responses] == [
            codes.CREATED,
            codes.OK,
            codes.NO_CONTENT,
            codes.NO_CONTENT,
            codes.NO_CONTENT,
        ]
        assert warmed_domains == [ResponseCacheDomain.ARTICLES] * 5
