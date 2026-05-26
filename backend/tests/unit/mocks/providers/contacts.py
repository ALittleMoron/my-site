from unittest.mock import Mock

from dishka import Provider, Scope, provide

from core.contacts.use_cases import AbstractContactsUseCase


class MockContactsProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_contacts_use_case(
        self,
    ) -> AbstractContactsUseCase:
        return Mock(spec=AbstractContactsUseCase)
