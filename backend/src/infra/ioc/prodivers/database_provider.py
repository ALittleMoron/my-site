from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from infra.postgresql import meta
from infra.postgresql.transactions import DatabaseTransactionState


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_transaction_state(self) -> DatabaseTransactionState:
        return DatabaseTransactionState(rollback_required=False)

    @provide(scope=Scope.REQUEST)
    async def provide_async_session(
        self,
        transaction_state: DatabaseTransactionState,
    ) -> AsyncGenerator[AsyncSession, BaseException | None]:
        async with meta.sessionmaker() as session:
            request_exception = yield session
            if request_exception is not None or transaction_state.rollback_required:
                await session.rollback()
            else:
                await session.commit()
