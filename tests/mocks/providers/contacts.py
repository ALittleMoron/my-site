from unittest.mock import Mock

from dishka import Provider, Scope, provide

from core.contacts.use_cases import AbstractCreateContactMeRequestUseCase


class MockContactsProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_create_contact_me_request_use_case(
        self,
    ) -> AbstractCreateContactMeRequestUseCase:
        mock = Mock(spec=AbstractCreateContactMeRequestUseCase)
        return mock
