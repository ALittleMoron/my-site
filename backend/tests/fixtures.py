from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers.factory import FactoryHelper
from tests.helpers.storage import StorageHelper


class FactoryFixture:
    factory: FactoryHelper

    @pytest.fixture(autouse=True)
    def _setup_factory(self) -> None:
        self.factory = FactoryHelper()


class StorageFixture:
    db_session: AsyncSession
    storage_helper: StorageHelper

    @pytest_asyncio.fixture(autouse=True)
    async def _setup_storage(self, session: AsyncSession) -> AsyncGenerator[None]:
        self.db_session = session
        self.storage_helper = StorageHelper(session=session)
        yield
        await self.db_session.rollback()
