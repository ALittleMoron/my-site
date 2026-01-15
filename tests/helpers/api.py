from dataclasses import dataclass
from typing import Any

from httpx import Response
from litestar.testing import TestClient


@dataclass(kw_only=True, frozen=True, slots=True)
class APIHelper:
    client: TestClient

    def get_health(self) -> Response:
        return self.client.get("/api/healthcheck")

    def get_competency_matrix_sheets(self) -> Response:
        return self.client.get("/api/competency-matrix/sheets")

    def get_competency_matrix_items(self, sheet_name: str = "") -> Response:
        return self.client.get(f"/api/competency-matrix/items", params={"sheetName": sheet_name})

    def get_competency_matrix_item(self, item_id: int) -> Response:
        return self.client.get(f"/api/competency-matrix/items/{item_id}")

    def post_create_contact_me_request(self, data: dict[str, Any]) -> Response:
        return self.client.post(f"/api/contacts", json=data)

    def get_presign_put_url(self, content_type: str) -> Response:
        return self.client.get(
            f"/api/files/presign-put",
            params={"contentType": content_type},
        )

    def post_login(self, data: dict[str, Any]) -> Response:
        return self.client.post("/api/auth/login", json=data)

    def post_logout(self) -> Response:
        return self.client.post("/api/auth/logout")
