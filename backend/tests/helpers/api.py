from dataclasses import dataclass
from typing import Any

from httpx import Response
from litestar.testing import TestClient


@dataclass(kw_only=True, frozen=True, slots=True)
class APIHelper:
    client: TestClient

    def get_health(self) -> Response:
        return self.client.get("/api/healthcheck")

    def get_search_competency_matrix_resources(
        self,
        search_name: str,
        limit: int | None = 10,
    ) -> Response:
        params: dict[str, str | int] = {"searchName": search_name}
        if limit is not None:
            params["limit"] = limit
        return self.client.get(
            "/api/competency-matrix/resources/search",
            params=params,
        )

    def get_competency_matrix_sheets(self) -> Response:
        return self.client.get("/api/competency-matrix/sheets")

    def get_competency_matrix_items(
        self,
        sheet_name: str = "",
        only_published: bool | None = True,
    ) -> Response:
        params: dict[str, str | bool] = {"sheetName": sheet_name}
        if only_published is not None:
            params["onlyPublished"] = only_published
        return self.client.get(
            "/api/competency-matrix/items",
            params=params,
        )

    def get_competency_matrix_item(self, pk: int, only_published: bool | None = True) -> Response:
        params: dict[str, bool] = {}
        if only_published is not None:
            params["onlyPublished"] = only_published
        return self.client.get(
            f"/api/competency-matrix/items/detail/{pk}",
            params=params,
        )

    def post_create_item(self, data: dict[str, Any]) -> Response:
        return self.client.post("/api/competency-matrix/items", json=data)

    def put_update_item(self, pk: int, data: dict[str, Any]) -> Response:
        return self.client.put(f"/api/competency-matrix/items/detail/{pk}", json=data)

    def delete_item(self, pk: int) -> Response:
        return self.client.delete(f"/api/competency-matrix/items/detail/{pk}")

    def post_set_draft_status_to_item(self, pk: int) -> Response:
        return self.client.post(f"/api/competency-matrix/items/detail/{pk}/set-draft")

    def post_set_published_status_to_item(self, pk: int) -> Response:
        return self.client.post(f"/api/competency-matrix/items/detail/{pk}/set-published")

    def get_notes(
        self,
        page: int | None = 1,
        page_size: int | None = 10,
        only_published: bool | None = True,
        tag_slug: str | None = None,
        published_from: str | None = None,
        published_to: str | None = None,
        search_query: str | None = None,
    ) -> Response:
        params: dict[str, str | int | bool] = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["pageSize"] = page_size
        if only_published is not None:
            params["onlyPublished"] = only_published
        if tag_slug is not None:
            params["tagSlug"] = tag_slug
        if published_from is not None:
            params["publishedFrom"] = published_from
        if published_to is not None:
            params["publishedTo"] = published_to
        if search_query is not None:
            params["searchQuery"] = search_query
        return self.client.get("/api/notes", params=params)

    def get_note(self, slug: str, only_published: bool | None = True) -> Response:
        params: dict[str, bool] = {}
        if only_published is not None:
            params["onlyPublished"] = only_published
        return self.client.get(f"/api/notes/detail/{slug}", params=params)

    def post_note_engaged_view(self, slug: str) -> Response:
        return self.client.post(f"/api/notes/detail/{slug}/analytics/engaged-view")

    def post_note_reaction(self, slug: str, data: dict[str, Any]) -> Response:
        return self.client.post(f"/api/notes/detail/{slug}/reaction", json=data)

    def get_note_stats(self, date_from: str | None, date_to: str | None) -> Response:
        params: dict[str, str] = {}
        if date_from is not None:
            params["dateFrom"] = date_from
        if date_to is not None:
            params["dateTo"] = date_to
        return self.client.get("/api/notes/stats", params=params)

    def get_notes_tree(self) -> Response:
        return self.client.get("/api/notes/tree")

    def post_create_note(self, data: dict[str, Any]) -> Response:
        return self.client.post("/api/notes", json=data)

    def put_update_note(self, slug: str, data: dict[str, Any]) -> Response:
        return self.client.put(f"/api/notes/detail/{slug}", json=data)

    def delete_note(self, slug: str) -> Response:
        return self.client.delete(f"/api/notes/detail/{slug}")

    def post_set_draft_status_to_note(self, slug: str) -> Response:
        return self.client.post(f"/api/notes/detail/{slug}/set-draft")

    def post_set_published_status_to_note(self, slug: str) -> Response:
        return self.client.post(f"/api/notes/detail/{slug}/set-published")

    def get_tags(self, include_deleted: bool | None = False) -> Response:
        params: dict[str, bool] = {}
        if include_deleted is not None:
            params["includeDeleted"] = include_deleted
        return self.client.get("/api/notes/tags", params=params)

    def get_search_tags(
        self,
        search_name: str,
        include_deleted: bool | None = False,
        limit: int | None = 10,
    ) -> Response:
        params: dict[str, str | int | bool] = {"searchName": search_name}
        if include_deleted is not None:
            params["includeDeleted"] = include_deleted
        if limit is not None:
            params["limit"] = limit
        return self.client.get("/api/notes/tags/search", params=params)

    def post_create_tag(self, data: dict[str, Any]) -> Response:
        return self.client.post("/api/notes/tags", json=data)

    def put_update_tag(self, tag_id: int, data: dict[str, Any]) -> Response:
        return self.client.put(f"/api/notes/tags/{tag_id}", json=data)

    def delete_tag(self, tag_id: int) -> Response:
        return self.client.delete(f"/api/notes/tags/{tag_id}")

    def post_restore_tag(self, tag_id: int) -> Response:
        return self.client.post(f"/api/notes/tags/{tag_id}/restore")

    def post_create_contact_me_request(self, data: dict[str, Any]) -> Response:
        return self.client.post("/api/contacts", json=data)

    def get_presign_put_url(self, content_type: str) -> Response:
        return self.client.get(
            "/api/files/presign-put",
            params={"contentType": content_type},
        )

    def post_login(self, data: dict[str, Any]) -> Response:
        return self.client.post("/api/auth/login", json=data)

    def post_logout(self) -> Response:
        return self.client.post("/api/auth/logout")

    def get_get_base_current_user_account(self) -> Response:
        return self.client.get("/api/account/base")
