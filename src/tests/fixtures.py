import pytest
from litestar import Litestar
from litestar.testing import TestClient

from app.database.storages import DatabaseStorage
from tests.helpers.api import ApiHelper
from tests.helpers.app import AppHelper
from tests.helpers.factory import FactoryHelper
from tests.helpers.storage import StorageHelper


class ApiFixture:
    api: ApiHelper
    app: AppHelper

    @pytest.fixture(autouse=True)
    def _setup_api(
        self,
        client: TestClient[Litestar],
    ) -> None:
        self.app = AppHelper()
        self.api = ApiHelper(client=client)


class FactoryFixture:
    factory: FactoryHelper

    @pytest.fixture(autouse=True)
    def _setup_factory(self) -> None:
        self.factory = FactoryHelper()


class StorageFixture:
    storage: DatabaseStorage
    storage_helper: StorageHelper

    @pytest.fixture(autouse=True)
    def _setup_storage(self, storage: DatabaseStorage) -> None:
        self.storage = storage
        self.storage_helper = StorageHelper(session=self.storage.session, use_flush=False)
