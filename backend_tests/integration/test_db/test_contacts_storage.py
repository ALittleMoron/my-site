import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend_tests.fixtures import FactoryFixture, StorageFixture
from infra.postgresql.storages.contacts import ContactMeDatabaseStorage


class TestContactMeStorage(FactoryFixture, StorageFixture):
    @pytest.fixture(autouse=True)
    async def setup(self, session: AsyncSession) -> None:
        self.storage = ContactMeDatabaseStorage(session=session)

    async def test_create_mentoring_contact_me(self) -> None:
        contact_me_id = uuid.uuid4()
        await self.storage.create_contact_me_request(
            form=self.factory.core.contact_me(
                contact_me_id=contact_me_id,
                name="NAME",
                email="example@mail.ru",
                telegram="@telegram",
                message="MESSAGE",
            ),
        )
        contact_me = await self.storage_helper.get_contact_me_by_id(contact_me_id=contact_me_id)
        assert contact_me == self.factory.core.contact_me(
            contact_me_id=contact_me_id,
            name="NAME",
            email="example@mail.ru",
            telegram="@telegram",
            message="MESSAGE",
        )
