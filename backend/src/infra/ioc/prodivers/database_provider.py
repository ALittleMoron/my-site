from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from infra.postgresql import meta


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_async_session(self) -> AsyncIterable[AsyncSession]:
        async with meta.sessionmaker() as session:
            yield session
            await session.commit()
