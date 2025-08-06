from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.blog.storages import BlogStorage
from core.blog.use_cases import (
    AbstractGetBlogPostUseCase,
    AbstractListBlogPostsUseCase,
    GetBlogPostUseCase,
    ListBlogPostsUseCase,
)
from db.storages.blog import BlogDatabaseStorage


class BlogProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_blog_storage(
        self,
        session: AsyncSession,
    ) -> BlogStorage:
        return BlogDatabaseStorage(session=session)

    @provide(scope=Scope.REQUEST)
    async def provide_get_blog_post_use_case(
        self,
        storage: BlogStorage,
    ) -> AbstractGetBlogPostUseCase:
        return GetBlogPostUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    async def provide_list_blog_posts_use_case(
        self,
        storage: BlogStorage,
    ) -> AbstractListBlogPostsUseCase:
        return ListBlogPostsUseCase(storage=storage)
