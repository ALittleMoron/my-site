from unittest.mock import Mock

import pytest

from core.blog.exceptions import BlogPostNotFoundError
from core.blog.storages import BlogStorage
from core.blog.use_cases import BlogUseCase
from core.enums import PublishStatusEnum
from tests.unit.fixtures import FactoryFixture


class TestBlogUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=BlogStorage)
        self.use_case = BlogUseCase(storage=self.storage)

    async def test_get_blog_post(self) -> None:
        slug = "test-post"
        expected_post = self.factory.core.blog_post(slug=slug)
        self.storage.get_post_by_slug.return_value = expected_post

        result = await self.use_case.get_blog_post(slug=slug)

        assert result == expected_post
        self.storage.get_post_by_slug.assert_called_once_with(slug=slug)

    async def test_get_blog_post_not_found_by_not_available(self) -> None:
        slug = "test-post"
        expected_post = self.factory.core.blog_post(
            slug=slug,
            publish_status=PublishStatusEnum.DRAFT,
        )
        self.storage.get_post_by_slug.return_value = expected_post

        with pytest.raises(BlogPostNotFoundError):
            await self.use_case.get_blog_post(slug=slug)

    async def test_get_blog_post_not_found_by_not_found(self) -> None:
        self.storage.get_post_by_slug.side_effect = BlogPostNotFoundError

        with pytest.raises(BlogPostNotFoundError):
            await self.use_case.get_blog_post(slug="some-slug")
