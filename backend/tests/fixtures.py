import pytest
from anydi import Container

from tests.client import SyncAndAsyncNinjaClient
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
    app: AppHelper
    api: APIHelper

    @pytest.fixture(autouse=True)
    def _setup_api(
        self,
        client: SyncAndAsyncNinjaClient,
        test_container: Container,
    ) -> None:
        self.api = APIHelper(client=client)
        self.app = AppHelper(container=test_container)


class StorageFixture:
    db: StorageHelper

    @pytest.fixture(autouse=True)
    def _setup_storage(self) -> None:
        self.db = StorageHelper()
