from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.contacts.storages import ContactMeStorage
from core.contacts.use_cases import (
    AbstractCreateContactMeRequestUseCase,
    CreateContactMeRequestUseCase,
)
from db.storages.contacts import ContactMeDatabaseStorage
from entrypoints.litestar.views.contacts.context_converters import ContactsContextConverter


class ContactsProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_context_converter(self) -> ContactsContextConverter:
        return ContactsContextConverter()

    @provide(scope=Scope.REQUEST)
    async def provide_contact_me_storage(
        self,
        session: AsyncSession,
    ) -> ContactMeStorage:
        return ContactMeDatabaseStorage(session=session)

    @provide(scope=Scope.REQUEST)
    async def provide_create_contact_me_request_use_case(
        self,
        storage: ContactMeStorage,
    ) -> AbstractCreateContactMeRequestUseCase:
        return CreateContactMeRequestUseCase(storage=storage)
