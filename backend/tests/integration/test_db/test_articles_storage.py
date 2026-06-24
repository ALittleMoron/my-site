from datetime import date

import pytest
import pytest_asyncio

from core.articles.exceptions import ArticleNotFoundError, TagNotFoundError
from core.articles.schemas import ArticleFilters
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import IntId
from infra.postgresql.storages.articles import ArticlesDatabaseStorage
from tests.test_cases import StorageTestCase


class TestArticlesDatabaseStorage(StorageTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.storage = ArticlesDatabaseStorage(session=self.db_session)

    async def test_get_article_by_slug_success(self) -> None:
        tag = self.factory.core.tag(tag_id=IntId(1), slug="python")
        deleted_tag = self.factory.core.tag(
            tag_id=IntId(2),
            name="Deleted",
            slug="deleted",
            deleted_at="2024-01-01T00:00:00",
        )
        await self.storage_helper.create_tags(tags=[tag, deleted_tag])
        await self.storage_helper.create_article(
            article=self.factory.core.article(
                title="Test Article",
                content="Test content",
                slug="test-article",
                folder="Python",
                tags=[tag, deleted_tag],
                publish_status=PublishStatusEnum.PUBLISHED,
                published_at="2024-01-01T00:00:00",
                created_at="2024-01-01T00:00:00",
                updated_at="2024-01-01T00:00:00",
            ),
        )

        public_result = await self.storage.get_article_by_slug(
            slug="test-article",
            include_deleted_tags=False,
        )
        admin_result = await self.storage.get_article_by_slug(
            slug="test-article",
            include_deleted_tags=True,
        )

        assert public_result.localized_title(language=LanguageEnum.RU) == "Test Article"
        assert self.collections.slugs(public_result.tags) == ["python"]
        assert self.collections.slugs(admin_result.tags) == ["python", "deleted"]

    async def test_get_article_by_slug_returns_canonical_translations(self) -> None:
        await self.storage_helper.create_article(
            article=self.factory.core.article(
                title_ru="Русская статья",
                title_en="English article",
                content_ru="Русское содержимое",
                content_en="English content",
                folder_ru="Русская папка",
                folder_en="English folder",
                slug="localized-article",
                seo_title_ru="SEO русская статья",
                seo_title_en="SEO English article",
                seo_description_ru="Описание русской статьи",
                seo_description_en="English article description",
                cover_image_url="https://example.com/cover.jpg",
                cover_image_alt_ru="Обложка",
                cover_image_alt_en="Cover",
            ),
        )

        result = await self.storage.get_article_by_slug(
            slug="localized-article",
            include_deleted_tags=False,
        )

        assert not hasattr(result, "title")
        assert not hasattr(result, "content")
        assert not hasattr(result, "folder")
        assert result.localized_title(language=LanguageEnum.RU) == "Русская статья"
        assert result.localized_content(language=LanguageEnum.RU) == "Русское содержимое"
        assert result.localized_folder(language=LanguageEnum.RU) == "Русская папка"
        assert result.localized_title(language=LanguageEnum.EN) == "English article"
        assert result.localized_content(language=LanguageEnum.EN) == "English content"
        assert result.localized_folder(language=LanguageEnum.EN) == "English folder"
        assert result.metadata.seo_title_ru == "SEO русская статья"
        assert result.metadata.seo_title_en == "SEO English article"
        assert result.metadata.seo_description_ru == "Описание русской статьи"
        assert result.metadata.seo_description_en == "English article description"
        assert result.metadata.cover_image_url == "https://example.com/cover.jpg"
        assert result.metadata.cover_image_alt_ru == "Обложка"
        assert result.metadata.cover_image_alt_en == "Cover"

    async def test_get_article_by_slug_not_found(self) -> None:
        with pytest.raises(ArticleNotFoundError):
            await self.storage.get_article_by_slug(
                slug="non-existent",
                include_deleted_tags=False,
            )

    async def test_list_articles_filters_by_active_tag_and_published_status(self) -> None:
        python = self.factory.core.tag(tag_id=IntId(1), slug="python")
        draft_tag = self.factory.core.tag(tag_id=IntId(2), slug="draft")
        await self.storage_helper.create_tags(tags=[python, draft_tag])
        await self.storage_helper.create_articles(
            articles=[
                self.factory.core.article(
                    title="Published Python",
                    slug="published-python",
                    tags=[python],
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-01T00:00:00",
                    created_at="2024-02-01T00:00:00",
                    updated_at="2024-02-01T00:00:00",
                ),
                self.factory.core.article(
                    title="Draft Python",
                    slug="draft-python",
                    tags=[python],
                    publish_status=PublishStatusEnum.DRAFT,
                    created_at="2024-03-01T00:00:00",
                    updated_at="2024-03-01T00:00:00",
                ),
                self.factory.core.article(
                    title="Other",
                    slug="other",
                    tags=[draft_tag],
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-04-01T00:00:00",
                    created_at="2024-04-01T00:00:00",
                    updated_at="2024-04-01T00:00:00",
                ),
            ],
        )

        articles, total_count = await self.storage.list_articles(
            filters=ArticleFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug="python",
                published_from=None,
                published_to=None,
                search_query=None,
            ),
        )

        assert self.collections.slugs(articles) == ["published-python"]
        assert total_count == 1

    async def test_list_articles_filters_published_without_pagination_or_tags_for_seo(self) -> None:
        await self.storage_helper.create_articles(
            articles=[
                self.factory.core.article(
                    title="Older published",
                    slug="older-published",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-01T00:00:00",
                    created_at="2024-02-01T00:00:00",
                    updated_at="2024-02-02T00:00:00",
                ),
                self.factory.core.article(
                    title="Draft",
                    slug="draft",
                    publish_status=PublishStatusEnum.DRAFT,
                    published_at=None,
                    created_at="2024-02-03T00:00:00",
                    updated_at="2024-02-03T00:00:00",
                ),
                self.factory.core.article(
                    title="Newer published",
                    slug="newer-published",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-03-01T00:00:00",
                    created_at="2024-03-01T00:00:00",
                    updated_at="2024-03-02T00:00:00",
                ),
            ],
        )

        articles, total_count = await self.storage.list_articles(
            filters=ArticleFilters(
                only_published=True,
                include_tags=False,
                order_for_seo=True,
            ),
        )

        assert self.collections.slugs(articles) == ["newer-published", "older-published"]
        assert [list(article.tags) for article in articles] == [[], []]
        assert total_count == 2

    async def test_list_articles_sorts_published_before_drafts_for_admin(self) -> None:
        await self.storage_helper.create_articles(
            articles=[
                self.factory.core.article(
                    title="Draft",
                    slug="draft",
                    publish_status=PublishStatusEnum.DRAFT,
                    created_at="2024-05-01T00:00:00",
                    updated_at="2024-05-01T00:00:00",
                ),
                self.factory.core.article(
                    title="Older Published",
                    slug="older-published",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-01-01T00:00:00",
                    created_at="2024-01-01T00:00:00",
                    updated_at="2024-01-01T00:00:00",
                ),
                self.factory.core.article(
                    title="Newer Published",
                    slug="newer-published",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-04-01T00:00:00",
                    created_at="2024-04-01T00:00:00",
                    updated_at="2024-04-01T00:00:00",
                ),
            ],
        )

        articles, _total_count = await self.storage.list_articles(
            filters=ArticleFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=False,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query=None,
            ),
        )

        assert self.collections.slugs(articles) == [
            "newer-published",
            "older-published",
            "draft",
        ]

    async def test_list_articles_filters_by_inclusive_publish_date_range(self) -> None:
        await self.storage_helper.create_articles(
            articles=[
                self.factory.core.article(
                    title="Before",
                    slug="before",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-01-31T23:59:59",
                    created_at="2024-01-31T23:59:59",
                    updated_at="2024-01-31T23:59:59",
                ),
                self.factory.core.article(
                    title="Range Start",
                    slug="range-start",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-01T00:00:00",
                    created_at="2024-02-01T00:00:00",
                    updated_at="2024-02-01T00:00:00",
                ),
                self.factory.core.article(
                    title="Range End",
                    slug="range-end",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-29T23:59:59",
                    created_at="2024-02-29T23:59:59",
                    updated_at="2024-02-29T23:59:59",
                ),
                self.factory.core.article(
                    title="After",
                    slug="after",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-03-01T00:00:00",
                    created_at="2024-03-01T00:00:00",
                    updated_at="2024-03-01T00:00:00",
                ),
                self.factory.core.article(
                    title="Draft",
                    slug="draft",
                    publish_status=PublishStatusEnum.DRAFT,
                    created_at="2024-02-15T00:00:00",
                    updated_at="2024-02-15T00:00:00",
                ),
            ],
        )

        articles, total_count = await self.storage.list_articles(
            filters=ArticleFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=False,
                tag_slug=None,
                published_from=date(2024, 2, 1),
                published_to=date(2024, 2, 29),
                search_query=None,
            ),
        )

        assert self.collections.slugs(articles) == ["range-end", "range-start"]
        assert total_count == 2

    async def test_list_articles_searches_by_title_and_content(self) -> None:
        await self.storage_helper.create_articles(
            articles=[
                self.factory.core.article(
                    title="PostgreSQL full text search",
                    content="Indexing articles without a table scan.",
                    slug="title-match",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-05-01T00:00:00",
                ),
                self.factory.core.article(
                    title="Dependency injection",
                    content="Dishka providers wire use cases to storage adapters.",
                    slug="content-match",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-04-01T00:00:00",
                ),
                self.factory.core.article(
                    title="Unrelated",
                    content="No matching terms here.",
                    slug="unrelated",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-06-01T00:00:00",
                ),
            ],
        )

        title_articles, _title_total_count = await self.storage.list_articles(
            filters=ArticleFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query="full text",
            ),
        )
        content_articles, _content_total_count = await self.storage.list_articles(
            filters=ArticleFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query="dishka providers",
            ),
        )

        assert self.collections.slugs(title_articles) == ["title-match"]
        assert self.collections.slugs(content_articles) == ["content-match"]

    async def test_list_articles_searches_only_requested_language_vector(self) -> None:
        await self.storage_helper.create_articles(
            articles=[
                self.factory.core.article(
                    title_ru="Очереди задач",
                    title_en="Task queues",
                    content_ru="Фоновая обработка заданий.",
                    content_en="Background job processing.",
                    slug="task-queues",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-05-01T00:00:00",
                ),
                self.factory.core.article(
                    title_ru="Индексы PostgreSQL",
                    title_en="Database indexes",
                    content_ru="Поиск по документам.",
                    content_en="Query planning details.",
                    slug="database-indexes",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-04-01T00:00:00",
                ),
            ],
        )

        ru_articles, _ru_total_count = await self.storage.list_articles(
            filters=ArticleFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query="документам",
            ),
        )
        en_articles, _en_total_count = await self.storage.list_articles(
            filters=ArticleFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.EN,
                only_published=True,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query="background",
            ),
        )

        assert self.collections.slugs(ru_articles) == ["database-indexes"]
        assert self.collections.slugs(en_articles) == ["task-queues"]

    async def test_list_articles_composes_tag_date_and_search_filters(self) -> None:
        python = self.factory.core.tag(tag_id=IntId(1), slug="python")
        database = self.factory.core.tag(tag_id=IntId(2), slug="database")
        await self.storage_helper.create_tags(tags=[python, database])
        await self.storage_helper.create_articles(
            articles=[
                self.factory.core.article(
                    title="Python database indexing",
                    content="PostgreSQL search vectors for articles.",
                    slug="match",
                    tags=[python],
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-10T00:00:00",
                ),
                self.factory.core.article(
                    title="Python old indexing",
                    content="PostgreSQL search vectors for articles.",
                    slug="old",
                    tags=[python],
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-01-10T00:00:00",
                ),
                self.factory.core.article(
                    title="Database indexing",
                    content="PostgreSQL search vectors for articles.",
                    slug="wrong-tag",
                    tags=[database],
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-10T00:00:00",
                ),
            ],
        )

        articles, _total_count = await self.storage.list_articles(
            filters=ArticleFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug="python",
                published_from=date(2024, 2, 1),
                published_to=date(2024, 2, 29),
                search_query="search vectors",
            ),
        )

        assert self.collections.slugs(articles) == ["match"]

    async def test_list_tree_groups_folders_and_hides_drafts_for_public(self) -> None:
        await self.storage_helper.create_articles(
            articles=[
                self.factory.core.article(
                    title="B Article",
                    slug="b-article",
                    folder="Backend",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-01-01T00:00:00",
                ),
                self.factory.core.article(
                    title="A Article",
                    slug="a-article",
                    folder="Architecture",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-01T00:00:00",
                ),
                self.factory.core.article(
                    title="Draft",
                    slug="draft",
                    folder="Architecture",
                    publish_status=PublishStatusEnum.DRAFT,
                ),
            ],
        )

        public_items = await self.storage.list_tree_items(
            only_published=True,
            language=LanguageEnum.RU,
        )
        admin_items = await self.storage.list_tree_items(
            only_published=False,
            language=LanguageEnum.RU,
        )

        assert [(item.folder, item.slug) for item in public_items] == [
            ("Architecture", "a-article"),
            ("Backend", "b-article"),
        ]
        assert [(item.folder, item.slug) for item in admin_items] == [
            ("Architecture", "a-article"),
            ("Architecture", "draft"),
            ("Backend", "b-article"),
        ]

    async def test_update_article_publish_status_sets_first_published_at_only_once(self) -> None:
        await self.storage_helper.create_article(
            article=self.factory.core.article(slug="draft", publish_status=PublishStatusEnum.DRAFT),
        )

        await self.storage.update_article_publish_status(
            slug="draft",
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        first = await self.storage.get_article_by_slug(
            slug="draft",
            include_deleted_tags=False,
        )
        await self.storage.update_article_publish_status(
            slug="draft",
            publish_status=PublishStatusEnum.DRAFT,
        )
        await self.storage.update_article_publish_status(
            slug="draft",
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        second = await self.storage.get_article_by_slug(
            slug="draft",
            include_deleted_tags=False,
        )

        assert first.published_at is not None
        assert second.published_at == first.published_at

    async def test_tag_soft_delete_and_restore(self) -> None:
        tag = self.factory.core.tag(tag_id=IntId(1), slug="python")
        await self.storage.create_tag(tag=tag)

        await self.storage.soft_delete_tag(tag_id=IntId(1))
        active_tags = await self.storage.list_tags(
            include_deleted=False,
            language=LanguageEnum.RU,
        )
        deleted_tags = await self.storage.list_tags(
            include_deleted=True,
            language=LanguageEnum.RU,
        )
        await self.storage.restore_tag(tag_id=IntId(1))
        restored_tags = await self.storage.list_tags(
            include_deleted=False,
            language=LanguageEnum.RU,
        )

        assert active_tags.values == []
        assert deleted_tags.values[0].deleted_at is not None
        assert self.collections.slugs(restored_tags) == ["python"]

    async def test_search_tags_matches_typo(self) -> None:
        await self.storage_helper.create_tags(
            tags=[
                self.factory.core.tag(tag_id=IntId(1), name="Python", slug="python"),
                self.factory.core.tag(tag_id=IntId(2), name="Django", slug="django"),
            ],
        )

        tags = await self.storage.search_tags(
            search_name="pythno",
            include_deleted=False,
            limit=10,
            language=LanguageEnum.EN,
        )

        assert self.collections.names_en(tags) == ["Python"]

    async def test_search_tags_matches_secondary_language_name(self) -> None:
        await self.storage_helper.create_tags(
            tags=[
                self.factory.core.tag(
                    tag_id=IntId(1),
                    name_ru="Базы данных",
                    name_en="Databases",
                    slug="databases",
                ),
            ],
        )

        tags = await self.storage.search_tags(
            search_name="базы",
            include_deleted=False,
            limit=10,
            language=LanguageEnum.EN,
        )

        assert self.collections.names_en(tags) == ["Databases"]

    async def test_search_tags_ranks_active_language_matches_before_slug_matches(self) -> None:
        await self.storage_helper.create_tags(
            tags=[
                self.factory.core.tag(
                    tag_id=IntId(1),
                    name="Package tooling",
                    slug="python-packages",
                ),
                self.factory.core.tag(
                    tag_id=IntId(2),
                    name="Python",
                    slug="language",
                ),
                self.factory.core.tag(
                    tag_id=IntId(3),
                    name="Python internals",
                    slug="runtime",
                ),
            ],
        )

        tags = await self.storage.search_tags(
            search_name="python",
            include_deleted=False,
            limit=10,
            language=LanguageEnum.EN,
        )

        assert self.collections.names_en(tags)[:2] == ["Python", "Python internals"]

    async def test_search_tags_respects_limit(self) -> None:
        await self.storage_helper.create_tags(
            tags=[
                self.factory.core.tag(tag_id=IntId(1), name="Limit A", slug="limit-a"),
                self.factory.core.tag(tag_id=IntId(2), name="Limit B", slug="limit-b"),
                self.factory.core.tag(tag_id=IntId(3), name="Limit C", slug="limit-c"),
            ],
        )

        tags = await self.storage.search_tags(
            search_name="limit",
            include_deleted=False,
            limit=2,
            language=LanguageEnum.EN,
        )

        assert len(tags) == 2

    async def test_search_tags_excludes_deleted_tags(self) -> None:
        await self.storage_helper.create_tags(
            tags=[
                self.factory.core.tag(tag_id=IntId(1), name="Python", slug="python"),
                self.factory.core.tag(
                    tag_id=IntId(2),
                    name="Python deleted",
                    slug="python-deleted",
                    deleted_at="2026-01-04T03:04:05",
                ),
            ],
        )

        tags = await self.storage.search_tags(
            search_name="python",
            include_deleted=False,
            limit=10,
            language=LanguageEnum.EN,
        )

        assert self.collections.slugs(tags) == ["python"]

    async def test_update_unknown_tag_raises_not_found(self) -> None:
        with pytest.raises(TagNotFoundError):
            await self.storage.update_tag(
                tag=self.factory.core.tag(tag_id=IntId(999), name="Missing", slug="missing"),
            )
