from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from core.enums import StatusEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class BlogPost:
    id: UUID
    title: str
    content: str
    slug: str
    published_at: datetime | None
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    def is_available(self) -> bool:
        return self.status == StatusEnum.PUBLISHED


@dataclass(frozen=True, slots=True, kw_only=True)
class BlogPostList:
    total_count: int
    total_pages: int
    posts: list[BlogPost]

    def only_available(self) -> "BlogPostList":
        return BlogPostList(
            posts=[post for post in self.posts if post.is_available()],
            total_count=self.total_count,
            total_pages=self.total_pages,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class BlogPostFilters:
    page: int
    page_size: int
    only_available: bool

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
