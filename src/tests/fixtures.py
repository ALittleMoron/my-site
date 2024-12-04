import pytest
from litestar import Litestar
from litestar.testing import TestClient

from tests.helpers.api import ApiHelper


class ApiFixture:
    api: ApiHelper

    @pytest.fixture(autouse=True)
    def _setup_api(self, test_client: TestClient[Litestar]) -> None:
        self.api = ApiHelper()
        self.api.client = test_client
