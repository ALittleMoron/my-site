from unittest.mock import Mock

import pytest

from core.contacts.storages import ContactMeStorage
from core.contacts.use_cases import CreateContactMeRequestUseCase
from tests.fixtures import FactoryFixture


class TestCreateContactMeRequestUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=ContactMeStorage)
        self.use_case = CreateContactMeRequestUseCase(storage=self.storage)

    async def test(self) -> None:
        form = self.factory.core.contact_me(
            name="NAME",
            email="example@mail.ru",
            telegram="@telegram",
            message="MESSAGE",
        )
        await self.use_case.execute(form=form)
        self.storage.create_contact_me_request.assert_called_once_with(form=form)
