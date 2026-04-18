from unittest.mock import Mock

from dishka import Provider, Scope, provide

from core.account.storages import UserAccountStorage


class MockUserAccountProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_user_storage(self) -> UserAccountStorage:
        mock = Mock(spec=UserAccountStorage)
        return mock
