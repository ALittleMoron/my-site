from abc import ABC, abstractmethod
from uuid import UUID

from core.blog.schemas import BlogPost, BlogPostFilters, BlogPostList


class BlogStorage(ABC):
    @abstractmethod
    async def get_post_by_slug(self, slug: str) -> BlogPost:
        raise NotImplementedError

    @abstractmethod
    async def get_post_by_id(self, post_id: UUID) -> BlogPost:
        raise NotImplementedError

    @abstractmethod
    async def list_posts(self, filters: BlogPostFilters) -> BlogPostList:
        raise NotImplementedError
