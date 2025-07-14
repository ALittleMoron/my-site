from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.contacts.schemas import ContactMe
from core.contacts.storages import ContactMeStorage
from core.use_cases import UseCase


class AbstractCreateContactMePurchaseUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self, form: ContactMe) -> None:
        raise NotImplementedError


@dataclass(kw_only=True)
class CreateContactMePurchaseUseCase(AbstractCreateContactMePurchaseUseCase):
    storage: ContactMeStorage

    async def execute(self, form: ContactMe) -> None:
        await self.storage.create_contact_me_purchase(form=form)
