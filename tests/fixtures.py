import pytest
from dishka import AsyncContainer
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers.api import APIHelper
from tests.helpers.app import IocContainerHelper
from tests.helpers.factory import FactoryHelper
from tests.helpers.storage import StorageHelper


class FactoryFixture:
    factory: FactoryHelper

    @pytest.fixture(autouse=True)
    def _setup_factory(self) -> None:
        self.factory = FactoryHelper()


class ContainerFixture:
    container: IocContainerHelper

    @pytest.fixture(autouse=True)
    def _setup_app(
        self,
        container: AsyncContainer,
    ) -> None:
        self.container = IocContainerHelper(container=container)


class ApiFixture:
    api: APIHelper

    @pytest.fixture(autouse=True)
    def _setup_api(
        self,
        client: TestClient,
    ) -> None:
        self.api = APIHelper(client=client)


class StorageFixture:
    storage_helper: StorageHelper

    @pytest.fixture(autouse=True)
    def _setup_storage(self, session: AsyncSession) -> None:
        self.storage_helper = StorageHelper(session=session)
