from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from db.meta import sessionmaker


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_async_session(self) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session
            await session.commit()
