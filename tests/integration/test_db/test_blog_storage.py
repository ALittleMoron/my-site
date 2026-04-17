import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
import pytest_asyncio

from core.blog.exceptions import BlogPostNotFoundError
from core.blog.schemas import BlogPostFilters
from core.enums import PublishStatusEnum
from db.storages.blog import BlogDatabaseStorage
from tests.fixtures import StorageFixture, FactoryFixture


class TestBlogDatabaseStorage(StorageFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.storage = BlogDatabaseStorage(session=self.db_session)

    async def test_get_post_by_slug_success(self) -> None:
        await self.storage_helper.create_blog_post(
            blog_post=self.factory.core.blog_post(
                title="Test Post",
                content="Test content",
                slug="test-post",
                publish_status=PublishStatusEnum.PUBLISHED,
                published_at="2024-01-01T00:00:00",
                created_at="2024-01-01T00:00:00",
                updated_at="2024-01-01T00:00:00",
            ),
        )

        result = await self.storage.get_post_by_slug(slug="test-post")

        assert result.title == "Test Post"
        assert result.slug == "test-post"
        assert result.publish_status == PublishStatusEnum.PUBLISHED

    async def test_get_post_by_slug_not_found(self) -> None:
        storage = BlogDatabaseStorage(session=self.storage_helper.session)

        with pytest.raises(BlogPostNotFoundError):
            await storage.get_post_by_slug(slug="non-existent")

    async def test_list_posts(self) -> None:
        post_id_1 = uuid.uuid4()
        post_id_2 = uuid.uuid4()
        now = datetime.now(tz=ZoneInfo("Etc/UTC")).isoformat()
        await self.storage_helper.create_blog_posts(
            blog_posts=[
                self.factory.core.blog_post(
                    post_id=post_id_1,
                    slug="test-post-1",
                    published_at=now,
                    created_at=now,
                    updated_at=now,
                ),
                self.factory.core.blog_post(
                    post_id=post_id_2,
                    slug="test-post-2",
                    published_at=now,
                    created_at=now,
                    updated_at=now,
                ),
            ],
        )
        filters = BlogPostFilters(page=1, page_size=10, only_available=False)
        result = await self.storage.list_posts(filters=filters)
        assert result.posts == [
            self.factory.core.blog_post(
                post_id=post_id_1,
                slug="test-post-1",
                published_at=now,
                created_at=now,
                updated_at=now,
            ),
            self.factory.core.blog_post(
                post_id=post_id_2,
                slug="test-post-2",
                published_at=now,
                created_at=now,
                updated_at=now,
            ),
        ]

    async def test_list_posts_only_available(self) -> None:
        filters = BlogPostFilters(page=1, page_size=10, only_available=True)
        await self.storage_helper.create_blog_posts(
            blog_posts=[
                self.factory.core.blog_post(publish_status=PublishStatusEnum.PUBLISHED, slug=str(i))
                for i in range(5)
            ]
        )
        await self.storage_helper.create_blog_posts(
            blog_posts=[
                self.factory.core.blog_post(publish_status=PublishStatusEnum.DRAFT, slug=str(i + 5))
                for i in range(15)
            ]
        )
        result = await self.storage.list_posts(filters=filters)
        assert len(result.posts) == 5
        assert result.total_count == 5
        assert result.total_pages == 1

    async def test_list_posts_with_pagination(self) -> None:
        filters = BlogPostFilters(page=1, page_size=10, only_available=False)
        posts = [
            self.factory.core.blog_post(publish_status=PublishStatusEnum.PUBLISHED, slug=str(i))
            for i in range(15)
        ]
        await self.storage_helper.create_blog_posts(blog_posts=posts)

        result = await self.storage.list_posts(filters=filters)

        assert len(result.posts) == 10
        assert result.total_count == 15
        assert result.total_pages == 2
