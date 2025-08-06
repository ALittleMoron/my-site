import uuid
from datetime import datetime, UTC
from unittest.mock import Mock

import pytest

from core.blog.schemas import BlogPostFilters
from core.blog.storages import BlogStorage
from core.blog.use_cases import ListBlogPostsUseCase
from core.enums import StatusEnum
from tests.fixtures import FactoryFixture


class TestListBlogPostsUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=BlogStorage)
        self.use_case = ListBlogPostsUseCase(storage=self.storage)

    async def test_list_blog_posts(self) -> None:
        filters = BlogPostFilters(page=1, page_size=10, only_available=True)
        post_id = uuid.uuid4()
        now = datetime.now(tz=UTC).isoformat()
        self.storage.list_posts.return_value = self.factory.core.blog_post_list(
            posts=[
                self.factory.core.blog_post(
                    post_id=post_id,
                    status=StatusEnum.PUBLISHED,
                    published_at=now,
                    created_at=now,
                    updated_at=now,
                ),
            ],
            total_count=1,
            total_pages=1,
        )

        result = await self.use_case.execute(filters=filters)

        assert result == self.factory.core.blog_post_list(
            posts=[
                self.factory.core.blog_post(
                    post_id=post_id,
                    status=StatusEnum.PUBLISHED,
                    published_at=now,
                    created_at=now,
                    updated_at=now,
                ),
            ],
            total_count=1,
            total_pages=1,
        )
        self.storage.list_posts.assert_called_once_with(filters=filters)
