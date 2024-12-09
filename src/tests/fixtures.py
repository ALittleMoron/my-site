import pytest
from litestar import Litestar
from litestar.testing import TestClient

from app.database.storages import DatabaseStorage
from tests.helpers.api import ApiHelper
from tests.helpers.factory import FactoryHelper
from tests.helpers.storage import StorageHelper


class ApiFixture:
    mocked_api: ApiHelper

    @pytest.fixture(autouse=True)
    def _setup_api(
        self,
        client: TestClient[Litestar],
        mocked_client: TestClient[Litestar],
    ) -> None:
        self.api = ApiHelper(client=client)
        self.mocked_api = ApiHelper(client=mocked_client)


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
