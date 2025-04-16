from typing import AsyncIterable

from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from config.settings import settings


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_async_engine(self) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            settings.database.url.get_secret_value(),
            pool_pre_ping=settings.database.pool_pre_ping,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
        )
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    async def provide_async_session_maker(
        self,
        async_engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        session_maker = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=settings.database.expire_on_commit,
        )
        return session_maker

    @provide(scope=Scope.REQUEST)
    async def provide_async_session(
        self,
        async_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with async_sessionmaker() as session:
            yield session
            await session.commit()
