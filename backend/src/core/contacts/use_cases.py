from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.contacts.schemas import ContactMe
from core.contacts.storages import ContactMeStorage


class AbstractContactsUseCase(ABC):
    @abstractmethod
    async def create_contact_me_request(self, form: ContactMe) -> None:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class ContactsUseCase(AbstractContactsUseCase):
    storage: ContactMeStorage

    async def create_contact_me_request(self, form: ContactMe) -> None:
        await self.storage.create_contact_me_request(form=form)
