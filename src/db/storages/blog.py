from dataclasses import dataclass
from math import ceil
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.blog.exceptions import BlogPostNotFoundError
from core.blog.schemas import BlogPost, BlogPostFilters, BlogPostList
from core.blog.storages import BlogStorage
from core.enums import StatusEnum
from db.models import BlogPostModel


@dataclass(kw_only=True)
class BlogDatabaseStorage(BlogStorage):
    session: AsyncSession

    async def get_post_by_slug(self, slug: str) -> BlogPost:
        query = select(BlogPostModel).where(BlogPostModel.slug == slug)
        post_model = await self.session.scalar(query)
        if post_model is None:
            raise BlogPostNotFoundError
        return post_model.to_schema()

    async def get_post_by_id(self, post_id: UUID) -> BlogPost:
        query = select(BlogPostModel).where(BlogPostModel.id == post_id)
        post_model = await self.session.scalar(query)
        if post_model is None:
            raise BlogPostNotFoundError
        return post_model.to_schema()

    async def list_posts(self, filters: BlogPostFilters) -> BlogPostList:
        query = (
            select(BlogPostModel)
            .offset(filters.offset)
            .limit(filters.limit)
            .order_by(BlogPostModel.published_at.desc())
        )
        if filters.only_available:
            query = query.where(BlogPostModel.status == StatusEnum.PUBLISHED)
            total_count = (
                await self.session.scalar(
                    select(func.count(BlogPostModel.id)).where(
                        BlogPostModel.status == StatusEnum.PUBLISHED,
                    ),
                )
            ) or 0
        else:
            total_count = (await self.session.scalar(select(func.count(BlogPostModel.id)))) or 0

        post_models = await self.session.scalars(query)

        return BlogPostList(
            posts=[post_model.to_schema() for post_model in post_models],
            total_count=total_count,
            total_pages=ceil(total_count / filters.page_size) if total_count > 0 else 0,
        )
