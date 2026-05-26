from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.blog.exceptions import BlogPostNotFoundError
from core.blog.schemas import BlogPost, BlogPostFilters, BlogPostList
from core.blog.storages import BlogStorage


class AbstractBlogUseCase(ABC):
    @abstractmethod
    async def get_blog_post(self, slug: str) -> BlogPost:
        raise NotImplementedError

    @abstractmethod
    async def list_blog_posts(self, filters: BlogPostFilters) -> BlogPostList:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class BlogUseCase(AbstractBlogUseCase):
    storage: BlogStorage

    async def get_blog_post(self, slug: str) -> BlogPost:
        post = await self.storage.get_post_by_slug(slug=slug)
        if not post.is_available():
            raise BlogPostNotFoundError
        return post

    async def list_blog_posts(self, filters: BlogPostFilters) -> BlogPostList:
        return await self.storage.list_posts(filters=filters)
