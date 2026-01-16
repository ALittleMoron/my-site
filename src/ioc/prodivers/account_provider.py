from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.account.storages import UserAccountStorage
from db.storages.users import UserAccountDatabaseStorage


class UserAccountProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_user_storage(self, session: AsyncSession) -> UserAccountStorage:
        return UserAccountDatabaseStorage(session=session)
