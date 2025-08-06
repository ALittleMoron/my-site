from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.blog.exceptions import BlogPostNotFoundError
from core.blog.schemas import BlogPost, BlogPostFilters, BlogPostList
from core.blog.storages import BlogStorage
from core.use_cases import UseCase


class AbstractGetBlogPostUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self, slug: str) -> BlogPost:
        raise NotImplementedError


@dataclass(kw_only=True)
class GetBlogPostUseCase(AbstractGetBlogPostUseCase):
    storage: BlogStorage

    async def execute(self, slug: str) -> BlogPost:
        post = await self.storage.get_post_by_slug(slug=slug)
        if not post.is_available():
            raise BlogPostNotFoundError
        return post


class AbstractListBlogPostsUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self, filters: BlogPostFilters) -> BlogPostList:
        raise NotImplementedError


@dataclass(kw_only=True)
class ListBlogPostsUseCase(AbstractListBlogPostsUseCase):
    storage: BlogStorage

    async def execute(self, filters: BlogPostFilters) -> BlogPostList:
        return await self.storage.list_posts(filters=filters)
