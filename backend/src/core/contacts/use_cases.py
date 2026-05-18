from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.contacts.schemas import ContactMe
from core.contacts.storages import ContactMeStorage
from core.use_cases import UseCase


class AbstractCreateContactMeRequestUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self, form: ContactMe) -> None:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class CreateContactMeRequestUseCase(AbstractCreateContactMeRequestUseCase):
    storage: ContactMeStorage

    async def execute(self, form: ContactMe) -> None:
        await self.storage.create_contact_me_request(form=form)
