from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from core.articles.exceptions import ArticleNotFoundError, TagNotFoundError
from core.articles.schemas import (
    ArticleCreateParams,
    ArticleFilters,
    ArticleMetadata,
    ArticleTreeItemData,
    ArticleUpdateParams,
    PublishedArticleForSeo,
    PublishedArticlesForSeo,
    TagCreateParams,
    TagUpdateParams,
)
from core.articles.storages import ArticlesStorage
from core.articles.use_cases import ArticlesUseCase
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from tests.test_cases import TestCase


class TestArticlesUseCase(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=ArticlesStorage)
        self.use_case = ArticlesUseCase(storage=self.storage)

    async def test_list_articles_builds_page_from_storage_rows(self) -> None:
        filters = ArticleFilters(
            page=1,
            page_size=10,
            language=LanguageEnum.RU,
            only_published=True,
            tag_slug="python",
            published_from=None,
            published_to=None,
            search_query=None,
            include_tags=True,
        )
        article = self.factory.core.article(title="Published article", slug="published-article")
        self.storage.list_articles.return_value = ([article], 11)

        result = await self.use_case.list_articles(filters=filters)

        assert result.values == [article]
        assert result.total_count == 11
        assert result.total_pages == 2
        self.storage.list_articles.assert_called_once_with(filters=filters)

    async def test_list_articles_requires_pagination_before_storage_call(self) -> None:
        with pytest.raises(ValueError, match="pagination required"):
            await self.use_case.list_articles(filters=ArticleFilters())

        self.storage.list_articles.assert_not_called()

    async def test_list_published_articles_for_seo_uses_shared_storage_list_and_available_articles(
        self,
    ) -> None:
        first_updated_at = datetime(2026, 1, 1, tzinfo=UTC)
        first_article = self.factory.core.article(
            title="First article",
            slug="first-article",
            publish_status=PublishStatusEnum.PUBLISHED,
            updated_at="2026-01-01T00:00:00",
        )
        draft_article = self.factory.core.article(
            title="Draft article",
            slug="draft-article",
            publish_status=PublishStatusEnum.DRAFT,
            updated_at="2026-01-02T00:00:00",
        )
        self.storage.list_articles.return_value = ([first_article, draft_article], 2)

        result = await self.use_case.list_published_articles_for_seo()

        assert result == PublishedArticlesForSeo(
            values=[
                PublishedArticleForSeo(
                    slug="first-article",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    updated_at=first_updated_at,
                ),
            ],
        )
        self.storage.list_articles.assert_called_once_with(
            filters=ArticleFilters(only_published=True, include_tags=False, order_for_seo=True),
        )

    async def test_list_tree_builds_folders_from_storage_items(self) -> None:
        first_updated_at = datetime(2026, 1, 1, tzinfo=UTC)
        second_updated_at = datetime(2026, 1, 2, tzinfo=UTC)
        self.storage.list_tree_items.return_value = [
            ArticleTreeItemData(
                folder="Backend",
                title="Storage",
                slug="storage",
                publish_status=PublishStatusEnum.PUBLISHED,
                published_at=datetime(2026, 1, 1, tzinfo=UTC),
                updated_at=first_updated_at,
            ),
            ArticleTreeItemData(
                folder="Architecture",
                title="Boundaries",
                slug="boundaries",
                publish_status=PublishStatusEnum.DRAFT,
                published_at=None,
                updated_at=second_updated_at,
            ),
        ]

        result = await self.use_case.list_tree(
            only_published=False,
            language=LanguageEnum.EN,
        )

        assert [folder.folder for folder in result.folders] == ["Architecture", "Backend"]
        assert [item.slug for item in result.folders[0].articles] == ["boundaries"]
        assert [item.slug for item in result.folders[1].articles] == ["storage"]
        self.storage.list_tree_items.assert_called_once_with(
            only_published=False,
            language=LanguageEnum.EN,
        )

    async def test_get_article_rejects_draft_when_only_published(self) -> None:
        self.storage.get_article_by_slug.return_value = self.factory.core.article(
            slug="draft-article",
            publish_status=PublishStatusEnum.DRAFT,
        )

        with pytest.raises(ArticleNotFoundError):
            await self.use_case.get_article(
                slug="draft-article",
                only_published=True,
            )

    async def test_get_article_returns_draft_when_admin_requests_all_articles(self) -> None:
        expected = self.factory.core.article(
            slug="draft-article",
            publish_status=PublishStatusEnum.DRAFT,
        )
        self.storage.get_article_by_slug.return_value = expected

        result = await self.use_case.get_article(
            slug="draft-article",
            only_published=False,
        )

        assert result == expected
        self.storage.get_article_by_slug.assert_called_once_with(
            slug="draft-article",
            include_deleted_tags=True,
        )

    async def test_create_article_requires_all_tags_to_exist_and_be_active(self) -> None:
        tag_ids = [self.factory.core.hex_id(1), self.factory.core.hex_id(2)]
        params = ArticleCreateParams(
            id=self.factory.core.hex_id(10),
            slug="article",
            title_ru="Статья",
            title_en="Article",
            content_ru="Содержимое",
            content_en="Content",
            folder_ru="Питон",
            folder_en="Python",
            author_username="admin",
            publish_status=PublishStatusEnum.DRAFT,
            metadata=ArticleMetadata(
                seo_title_ru=None,
                seo_title_en=None,
                seo_description_ru=None,
                seo_description_en=None,
                cover_image_url=None,
                cover_image_alt_ru=None,
                cover_image_alt_en=None,
            ),
            tag_ids=tag_ids,
        )
        self.storage.get_tags_by_ids.return_value = self.factory.core.tags(
            values=[self.factory.core.tag(tag_id=1)],
        )

        with pytest.raises(TagNotFoundError):
            await self.use_case.create_article(params=params)

    async def test_create_article_persists_article_with_active_tags(self) -> None:
        tag_ids = [self.factory.core.hex_id(1)]
        article_id = self.factory.core.hex_id(10)
        params = ArticleCreateParams(
            id=article_id,
            slug="article",
            title_ru="Статья",
            title_en="Article",
            content_ru="Содержимое",
            content_en="Content",
            folder_ru="Питон",
            folder_en="Python",
            author_username="admin",
            publish_status=PublishStatusEnum.DRAFT,
            metadata=ArticleMetadata(
                seo_title_ru="SEO статья",
                seo_title_en="SEO article",
                seo_description_ru="Описание для поиска",
                seo_description_en="Search description",
                cover_image_url="https://example.com/cover.jpg",
                cover_image_alt_ru="Обложка",
                cover_image_alt_en="Cover",
            ),
            tag_ids=tag_ids,
        )
        tag = self.factory.core.tag(tag_id=1, slug="python")
        expected = self.factory.core.article(
            article_id=article_id,
            slug="article",
            title_ru="Статья",
            title_en="Article",
            content_ru="Содержимое",
            content_en="Content",
            folder_ru="Питон",
            folder_en="Python",
            author_username="admin",
            publish_status=PublishStatusEnum.DRAFT,
            metadata=ArticleMetadata(
                seo_title_ru="SEO статья",
                seo_title_en="SEO article",
                seo_description_ru="Описание для поиска",
                seo_description_en="Search description",
                cover_image_url="https://example.com/cover.jpg",
                cover_image_alt_ru="Обложка",
                cover_image_alt_en="Cover",
            ),
            tags=[tag],
        )
        self.storage.get_tags_by_ids.return_value = self.factory.core.tags(values=[tag])
        self.storage.create_article.return_value = expected

        result = await self.use_case.create_article(params=params)

        assert result == expected
        self.storage.create_article.assert_called_once()
        created_article = self.storage.create_article.call_args.kwargs["article"]
        assert not hasattr(created_article, "title")
        assert not hasattr(created_article, "content")
        assert not hasattr(created_article, "folder")
        assert created_article.localized_title(language=LanguageEnum.RU) == "Статья"
        assert created_article.localized_content(language=LanguageEnum.RU) == "Содержимое"
        assert created_article.localized_folder(language=LanguageEnum.RU) == "Питон"
        assert created_article.title_ru == "Статья"
        assert created_article.title_en == "Article"
        assert created_article.metadata == params.metadata
        assert created_article.author_username == "admin"
        assert created_article.tags.values == [tag]

    def test_article_create_params_builds_canonical_article(self) -> None:
        article_id = self.factory.core.hex_id(10)
        now = datetime(2026, 5, 31, 12, 0, tzinfo=UTC)
        tag = self.factory.core.tag(tag_id=1, slug="python")
        params = ArticleCreateParams(
            id=article_id,
            slug="article",
            title_ru="Статья",
            title_en="Article",
            content_ru="Содержимое",
            content_en="Content",
            folder_ru="Питон",
            folder_en="Python",
            author_username="admin",
            publish_status=PublishStatusEnum.PUBLISHED,
            metadata=ArticleMetadata(
                seo_title_ru=None,
                seo_title_en=None,
                seo_description_ru=None,
                seo_description_en=None,
                cover_image_url=None,
                cover_image_alt_ru=None,
                cover_image_alt_en=None,
            ),
            tag_ids=[self.factory.core.hex_id(1)],
        )

        article = params.to_article(now=now, tags=self.factory.core.tags(values=[tag]))

        assert not hasattr(article, "title")
        assert not hasattr(article, "content")
        assert not hasattr(article, "folder")
        assert article.localized_title(language=LanguageEnum.RU) == "Статья"
        assert article.localized_title(language=LanguageEnum.EN) == "Article"
        assert article.metadata == params.metadata
        assert article.published_at == now
        assert article.created_at == now
        assert article.updated_at == now
        assert article.tags.values == [tag]

    async def test_update_article_keeps_existing_author(self) -> None:
        tag = self.factory.core.tag(tag_id=1, slug="python")
        existing = self.factory.core.article(
            slug="old-article",
            author_username="original-author",
            tags=[tag],
        )
        params = ArticleUpdateParams(
            slug="new-article",
            title_ru="Новая",
            title_en="New",
            content_ru="Новый контент",
            content_en="New content",
            folder_ru="Архитектура",
            folder_en="Architecture",
            publish_status=PublishStatusEnum.PUBLISHED,
            metadata=ArticleMetadata(
                seo_title_ru="Новая SEO",
                seo_title_en="New SEO",
                seo_description_ru="Новое описание",
                seo_description_en="New description",
                cover_image_url=None,
                cover_image_alt_ru=None,
                cover_image_alt_en=None,
            ),
            tag_ids=[self.factory.core.hex_id(1)],
        )
        self.storage.get_article_by_slug.return_value = existing
        self.storage.get_tags_by_ids.return_value = self.factory.core.tags(values=[tag])
        self.storage.update_article.return_value = self.factory.core.article(
            title="New",
            slug="new-article",
            author_username="original-author",
            publish_status=PublishStatusEnum.PUBLISHED,
            tags=[tag],
        )

        await self.use_case.update_article(
            slug="old-article",
            params=params,
        )

        updated_article = self.storage.update_article.call_args.kwargs["article"]
        assert updated_article.id == existing.id
        assert updated_article.author_username == "original-author"
        assert updated_article.title_ru == "Новая"
        assert updated_article.title_en == "New"
        assert updated_article.metadata == params.metadata
        assert not hasattr(updated_article, "title")

    async def test_switch_publish_status_delegates_to_storage(self) -> None:
        await self.use_case.switch_article_publish_status(
            slug="article",
            publish_status=PublishStatusEnum.PUBLISHED,
        )

        self.storage.update_article_publish_status.assert_called_once_with(
            slug="article",
            publish_status=PublishStatusEnum.PUBLISHED,
        )

    async def test_create_tag_delegates_to_storage(self) -> None:
        params = TagCreateParams(
            id=self.factory.core.hex_id(1),
            name_ru="Питон",
            name_en="Python",
            slug="python",
        )
        expected = self.factory.core.tag(
            tag_id=1,
            name_ru="Питон",
            name_en="Python",
            slug="python",
        )
        self.storage.create_tag.return_value = expected

        result = await self.use_case.create_tag(params=params)

        assert result == expected
        self.storage.create_tag.assert_called_once_with(tag=expected)

    async def test_update_tag_delegates_to_storage(self) -> None:
        params = TagUpdateParams(
            name_ru="Питон обновлённый",
            name_en="Python Updated",
            slug="python-updated",
        )
        expected = self.factory.core.tag(
            tag_id=1,
            name_ru="Питон обновлённый",
            name_en="Python Updated",
            slug="python-updated",
        )
        self.storage.update_tag.return_value = expected

        result = await self.use_case.update_tag(
            tag_id=self.factory.core.hex_id(1),
            params=params,
        )

        assert result == expected
        self.storage.update_tag.assert_called_once_with(tag=expected)
