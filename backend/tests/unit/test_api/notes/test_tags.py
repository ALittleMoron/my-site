import pytest_asyncio
from httpx import codes

from core.auth.exceptions import ForbiddenError
from core.notes.exceptions import TagNotFoundError
from core.notes.schemas import TagCreateParams, TagUpdateParams
from core.types import IntId
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestTagsAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.tag_id = await self.container.get_random_int()
        self.use_case = await self.container.get_notes_use_case()

    def test_list_tags(self) -> None:
        self.use_case.list_tags.return_value = self.factory.core.tags(
            values=[
                self.factory.core.tag(tag_id=1, name="Python", slug="python"),
                self.factory.core.tag(
                    tag_id=2,
                    name="Old",
                    slug="old",
                    deleted_at="2026-01-04T03:04:05",
                ),
            ],
        )

        response = self.api.get_tags(include_deleted=True)

        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "tags": [
                {"id": 1, "name": "Python", "slug": "python", "deletedAt": None},
                {
                    "id": 2,
                    "name": "Old",
                    "slug": "old",
                    "deletedAt": "2026-01-04T03:04:05+00:00",
                },
            ],
        }
        self.use_case.list_tags.assert_called_once_with(include_deleted=True)

    def test_anonymous_cannot_list_deleted_tags(self) -> None:
        response = self.no_auth_api.get_tags(include_deleted=True)

        assert response.status_code == codes.FORBIDDEN
        assert response.json()["message"] == ForbiddenError.message
        self.use_case.list_tags.assert_not_called()

    def test_anonymous_cannot_list_deleted_tags_with_numeric_bool(self) -> None:
        response = self.no_auth_api.client.get("/api/notes/tags", params={"includeDeleted": "1"})

        assert response.status_code == codes.FORBIDDEN
        assert response.json()["message"] == ForbiddenError.message
        self.use_case.list_tags.assert_not_called()

    def test_search_tags(self) -> None:
        self.use_case.search_tags.return_value = self.factory.core.tags(
            values=[self.factory.core.tag(tag_id=1, name="Python", slug="python")],
        )

        response = self.api.get_search_tags(search_name="py", include_deleted=False, limit=5)

        assert response.status_code == codes.OK, response.content
        self.use_case.search_tags.assert_called_once_with(
            search_name="py",
            include_deleted=False,
            limit=5,
        )

    def test_create_tag(self) -> None:
        tag = self.factory.core.tag(tag_id=self.tag_id, name="Backend", slug="backend")
        self.use_case.create_tag.return_value = tag

        response = self.api.post_create_tag(data=self.factory.api.tag_request("Backend", "backend"))

        assert response.status_code == codes.CREATED, response.content
        assert response.json() == {
            "id": int(self.tag_id),
            "name": "Backend",
            "slug": "backend",
            "deletedAt": None,
        }
        self.use_case.create_tag.assert_called_once_with(
            params=TagCreateParams(id=self.tag_id, name="Backend", slug="backend"),
        )

    def test_update_tag(self) -> None:
        self.use_case.update_tag.return_value = self.factory.core.tag(
            tag_id=3,
            name="Architecture",
            slug="architecture",
        )

        response = self.api.put_update_tag(
            tag_id=3,
            data=self.factory.api.tag_request("Architecture", "architecture"),
        )

        assert response.status_code == codes.OK, response.content
        self.use_case.update_tag.assert_called_once_with(
            tag_id=IntId(3),
            params=TagUpdateParams(name="Architecture", slug="architecture"),
        )

    def test_delete_tag(self) -> None:
        response = self.api.delete_tag(tag_id=3)

        assert response.status_code == codes.NO_CONTENT
        self.use_case.soft_delete_tag.assert_called_once_with(tag_id=IntId(3))

    def test_restore_tag_not_found(self) -> None:
        self.use_case.restore_tag.side_effect = TagNotFoundError()

        response = self.api.post_restore_tag(tag_id=3)

        assert response.status_code == codes.NOT_FOUND
        assert response.json()["message"] == TagNotFoundError.message

    def test_restore_tag(self) -> None:
        response = self.api.post_restore_tag(tag_id=3)

        assert response.status_code == codes.NO_CONTENT
        self.use_case.restore_tag.assert_called_once_with(tag_id=IntId(3))
