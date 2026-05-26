from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.blog.storages import BlogStorage
from core.blog.use_cases import AbstractBlogUseCase, BlogUseCase
from infra.postgresql.storages.blog import BlogDatabaseStorage


class BlogProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_blog_storage(
        self,
        session: AsyncSession,
    ) -> BlogStorage:
        return BlogDatabaseStorage(session=session)

    @provide(scope=Scope.REQUEST)
    async def provide_blog_use_case(
        self,
        storage: BlogStorage,
    ) -> AbstractBlogUseCase:
        return BlogUseCase(storage=storage)
