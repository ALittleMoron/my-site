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

    def get_competency_matrix_items(
        self,
        sheet_name: str = "",
        only_published: bool = True,
    ) -> Response:
        return self.client.get(
            f"/api/competency-matrix/items",
            params={"sheetName": sheet_name, "onlyPublished": only_published},
        )

    def get_competency_matrix_item(self, item_id: int, only_published: bool = True) -> Response:
        return self.client.get(
            f"/api/competency-matrix/items/{item_id}",
            params={"onlyPublished": only_published},
        )

    def post_create_item(self, data: dict[str, Any]) -> Response:
        return self.client.post(f"/api/competency-matrix/items", json=data)

    def put_update_item(self, pk: int, data: dict[str, Any]) -> Response:
        return self.client.put(f"/api/competency-matrix/items/{pk}", json=data)

    def delete_item(self, pk: int) -> Response:
        return self.client.delete(f"/api/competency-matrix/items/{pk}")

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

    def get_get_base_current_user_account(self) -> Response:
        return self.client.get("/api/account/base")
