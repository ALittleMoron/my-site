import uuid
from datetime import date

import pytest_asyncio
from httpx import codes

from core.auth.exceptions import ForbiddenError
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.notes.schemas import NoteFilters, NotePublicStats, NotePublicStatsCollection
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestListNotesAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_notes_use_case()
        self.analytics_use_case = await self.container.get_note_analytics_use_case()
        self.analytics_use_case.get_public_stats.return_value = NotePublicStatsCollection(
            values=[],
        )

    def test_list_notes(self) -> None:
        tag = self.factory.core.tag(tag_id=1, name="Python", slug="python")
        note = self.factory.core.note(
            note_id=uuid.UUID(int=1),
            title="Typed notes",
            content="Typed notes content for excerpt.",
            slug="typed-notes",
            folder="Engineering",
            author_username="admin",
            publish_status=PublishStatusEnum.PUBLISHED,
            published_at="2026-01-02T03:04:05",
            created_at="2026-01-01T03:04:05",
            updated_at="2026-01-03T03:04:05",
            tags=[tag],
        )
        self.use_case.list_notes.return_value = self.factory.core.note_list(
            notes=[note],
            total_count=1,
            total_pages=1,
        )
        self.analytics_use_case.get_public_stats.return_value = NotePublicStatsCollection(
            values=[
                NotePublicStats(
                    note_id=note.id,
                    view_count=12,
                    reaction_counts=self.factory.core.note_reaction_counts(),
                ),
            ],
        )

        response = self.api.get_notes(page=1, page_size=10, only_published=True, tag_slug="python")

        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "totalCount": 1,
            "totalPages": 1,
            "notes": [
                {
                    "id": str(note.id),
                    "title": "Typed notes",
                    "slug": "typed-notes",
                    "folder": "Engineering",
                    "authorUsername": "admin",
                    "publishedAt": "2026-01-02T03:04:05+00:00",
                    "publishStatus": "Published",
                    "updatedAt": "2026-01-03T03:04:05+00:00",
                    "excerpt": "Typed notes content for excerpt.",
                    "viewCount": 12,
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
                    ],
                },
            ],
        }
        self.use_case.list_notes.assert_called_once_with(
            filters=NoteFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug="python",
                published_from=None,
                published_to=None,
                search_query=None,
            ),
        )

    def test_list_notes_with_publish_date_range_and_search_query(self) -> None:
        self.use_case.list_notes.return_value = self.factory.core.note_list(
            notes=[],
            total_count=0,
            total_pages=0,
        )

        response = self.api.get_notes(
            page=2,
            page_size=5,
            only_published=True,
            published_from="2026-01-01",
            published_to="2026-01-31",
            search_query="  typed notes  ",
        )

        assert response.status_code == codes.OK, response.content
        self.use_case.list_notes.assert_called_once_with(
            filters=NoteFilters(
                page=2,
                page_size=5,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug=None,
                published_from=date(2026, 1, 1),
                published_to=date(2026, 1, 31),
                search_query="typed notes",
            ),
        )

    def test_list_notes_requires_explicit_page(self) -> None:
        response = self.api.get_notes(page=None, page_size=10, only_published=True)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.list_notes.assert_not_called()

    def test_list_notes_requires_explicit_language(self) -> None:
        response = self.api.get_notes(page=1, page_size=10, only_published=True, language=None)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.list_notes.assert_not_called()

    def test_anonymous_cannot_request_all_notes(self) -> None:
        response = self.no_auth_api.get_notes(page=1, page_size=10, only_published=False)

        assert response.status_code == codes.FORBIDDEN
        assert response.json()["message"] == ForbiddenError.message
        self.use_case.list_notes.assert_not_called()
