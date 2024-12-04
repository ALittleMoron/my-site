import pytest
from httpx import Response
from litestar import Litestar
from litestar.testing import TestClient


class ApiHelper:
    __test__ = False

    client: TestClient[Litestar]

    @pytest.fixture(autouse=True)
    def _setup(self, test_client: TestClient[Litestar]) -> None:
        self.client = test_client

    def base_healthcheck(self) -> Response:
        return self.client.get("/api/health/base/")
