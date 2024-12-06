import pytest
from litestar import Litestar
from litestar.testing import TestClient

from tests.helpers.api import ApiHelper
from tests.helpers.app import AppHelper
from tests.helpers.factory import FactoryHelper


class ApiFixture:
    api: ApiHelper
    app: AppHelper

    @pytest.fixture(autouse=True)
    def _setup_api(
        self,
        test_app: Litestar,
        test_client: TestClient[Litestar],
    ) -> None:
        self.app = AppHelper(app=test_app)
        self.api = ApiHelper(client=test_client)


class FactoryFixture:
    factory: FactoryHelper

    @pytest.fixture(autouse=True)
    def _setup_factory(self) -> None:
        self.factory = FactoryHelper()
