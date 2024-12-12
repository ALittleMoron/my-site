from dataclasses import dataclass

from httpx import Response
from litestar import Litestar
from litestar.testing import TestClient


@dataclass(kw_only=True)
class ApiHelper:
    client: TestClient[Litestar]

    def base_healthcheck(self) -> Response:
        return self.client.get("/api/health/base/")

    def list_competency_matrix_items(self, sheet_id: int) -> Response:
        return self.client.get("/api/competencyMatrix/items/", params={"sheetId": sheet_id})

    def list_competency_matrix_sheets(self) -> Response:
        return self.client.get("/api/competencyMatrix/sheets/")

    def list_competency_matrix_subsections(self, sheet_id: int) -> Response:
        return self.client.get(
            "/api/competencyMatrix/subsections/",
            params={"sheetId": sheet_id},
        )
