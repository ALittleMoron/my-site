from core.account.storages import UserAccountStorage
from dishka import Provider, Scope, provide
from infra.postgresql.storages.users import UserAccountDatabaseStorage
from sqlalchemy.ext.asyncio import AsyncSession


class UserAccountProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_user_storage(self, session: AsyncSession) -> UserAccountStorage:
        return UserAccountDatabaseStorage(session=session)
