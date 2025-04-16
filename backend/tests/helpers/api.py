from dataclasses import dataclass

from fastapi.testclient import TestClient
from httpx import Response


@dataclass(kw_only=True, frozen=True, slots=True)
class APIHelper:
    client: TestClient

    def get_health(self) -> Response:
        return self.client.get("/api/health")

    def get_competency_matrix_sheets(self) -> Response:
        return self.client.get("/api/competency-matrix/sheets")

    def get_competency_matrix_items(self, sheet_name: str = "") -> Response:
        return self.client.get(f"/api/competency-matrix/items", params={"sheetName": sheet_name})

    def get_competency_matrix_item(self, item_id: int) -> Response:
        return self.client.get(f"/api/competency-matrix/items/{item_id}")
