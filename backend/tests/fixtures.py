import pytest
from dishka import AsyncContainer
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers.api import APIHelper
from tests.helpers.app import AppHelper
from tests.helpers.factory import FactoryHelper
from tests.helpers.storage import StorageHelper


class FactoryFixture:
    factory: FactoryHelper

    @pytest.fixture(autouse=True)
    def _setup_factory(self) -> None:
        self.factory = FactoryHelper()


class ApiFixture:
    api: APIHelper
    app: AppHelper

    @pytest.fixture(autouse=True)
    def _setup_api(
        self,
        client: TestClient,
        container: AsyncContainer,
    ) -> None:
        self.api = APIHelper(client=client)
        self.app = AppHelper(container=container)


class StorageFixture:
    db: StorageHelper

    @pytest.fixture(autouse=True)
    def _setup_storage(self, session: AsyncSession) -> None:
        self.db = StorageHelper(session=session)
