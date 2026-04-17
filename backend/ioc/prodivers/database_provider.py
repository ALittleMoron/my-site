from collections.abc import AsyncIterable

from db.meta import sessionmaker
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_async_session(self) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session
            await session.commit()
