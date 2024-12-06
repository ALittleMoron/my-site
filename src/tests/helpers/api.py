from dataclasses import dataclass

from httpx import Response
from litestar import Litestar
from litestar.testing import TestClient


@dataclass(kw_only=True)
class ApiHelper:
    client: TestClient[Litestar]

    def base_healthcheck(self) -> Response:
        return self.client.get("/api/health/base/")

    def list_competency_matrix(self) -> Response:
        return self.client.get("/api/competencyMatrix/items/")
