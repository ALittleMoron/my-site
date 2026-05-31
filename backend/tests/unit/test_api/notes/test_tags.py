import pytest_asyncio
from httpx import codes

from core.auth.exceptions import ForbiddenError
from core.i18n.enums import LanguageEnum
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
                {
                    "id": 1,
                    "name": "Python",
                    "slug": "python",
                    "deletedAt": None,
                    "translations": {
                        "ru": {"name": "Python"},
                        "en": {"name": "Python"},
                    },
                },
                {
                    "id": 2,
                    "name": "Old",
                    "slug": "old",
                    "deletedAt": "2026-01-04T03:04:05+00:00",
                    "translations": {
                        "ru": {"name": "Old"},
                        "en": {"name": "Old"},
                    },
                },
            ],
        }
        self.use_case.list_tags.assert_called_once_with(
            include_deleted=True,
            language=LanguageEnum.RU,
        )

    def test_list_tags_requires_explicit_language(self) -> None:
        response = self.api.get_tags(include_deleted=False, language=None)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.list_tags.assert_not_called()

    def test_anonymous_cannot_list_deleted_tags(self) -> None:
        response = self.no_auth_api.get_tags(include_deleted=True)

        assert response.status_code == codes.FORBIDDEN
        assert response.json()["message"] == ForbiddenError.message
        self.use_case.list_tags.assert_not_called()

    def test_anonymous_cannot_list_deleted_tags_with_numeric_bool(self) -> None:
        response = self.no_auth_api.client.get(
            "/api/notes/tags",
            params={"includeDeleted": "1", "language": "ru"},
        )

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
            language=LanguageEnum.RU,
        )

    def test_create_tag(self) -> None:
        tag = self.factory.core.tag(
            tag_id=self.tag_id,
            name="Бэкенд",
            name_ru="Бэкенд",
            name_en="Backend",
            slug="backend",
        )
        self.use_case.create_tag.return_value = tag

        response = self.api.post_create_tag(
            data=self.factory.api.tag_request(name_ru="Бэкенд", name_en="Backend", slug="backend"),
        )

        assert response.status_code == codes.CREATED, response.content
        assert response.json() == {
            "id": int(self.tag_id),
            "name": "Бэкенд",
            "slug": "backend",
            "deletedAt": None,
            "translations": {
                "ru": {"name": "Бэкенд"},
                "en": {"name": "Backend"},
            },
        }
        self.use_case.create_tag.assert_called_once_with(
            params=TagCreateParams(
                id=self.tag_id,
                name_ru="Бэкенд",
                name_en="Backend",
                slug="backend",
            ),
        )

    def test_update_tag(self) -> None:
        self.use_case.update_tag.return_value = self.factory.core.tag(
            tag_id=3,
            name="Архитектура",
            name_ru="Архитектура",
            name_en="Architecture",
            slug="architecture",
        )

        response = self.api.put_update_tag(
            tag_id=3,
            data=self.factory.api.tag_request(
                name_ru="Архитектура",
                name_en="Architecture",
                slug="architecture",
            ),
        )

        assert response.status_code == codes.OK, response.content
        self.use_case.update_tag.assert_called_once_with(
            tag_id=IntId(3),
            params=TagUpdateParams(
                name_ru="Архитектура",
                name_en="Architecture",
                slug="architecture",
            ),
        )

    def test_create_tag_requires_all_translation_fields(self) -> None:
        data = self.factory.api.tag_request()
        del data["translations"]["en"]["name"]

        response = self.api.post_create_tag(data=data)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.create_tag.assert_not_called()

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
