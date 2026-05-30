import uuid
from datetime import UTC, datetime

import pytest_asyncio
from httpx import codes

from core.auth.exceptions import ForbiddenError
from core.enums import PublishStatusEnum
from core.notes.exceptions import NoteNotFoundError
from core.notes.schemas import (
    NotePublicStats,
    NotePublicStatsCollection,
    NoteReactionCounts,
    NoteTree,
    NoteTreeFolder,
    NoteTreeItem,
)
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestNoteDetailAndTreeAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_notes_use_case()
        self.analytics_use_case = await self.container.get_note_analytics_use_case()
        self.analytics_use_case.get_public_stats.return_value = NotePublicStatsCollection(
            values=[],
        )

    def test_get_note(self) -> None:
        deleted_tag = self.factory.core.tag(
            tag_id=2,
            name="Old",
            slug="old",
            deleted_at="2026-01-04T03:04:05",
        )
        note = self.factory.core.note(
            note_id=uuid.UUID(int=1),
            title="Detail note",
            content="# Markdown detail",
            slug="detail-note",
            folder="General",
            author_username="admin",
            publish_status=PublishStatusEnum.PUBLISHED,
            published_at="2026-01-02T03:04:05",
            created_at="2026-01-01T03:04:05",
            updated_at="2026-01-03T03:04:05",
            tags=[deleted_tag],
        )
        self.use_case.get_note.return_value = note
        self.analytics_use_case.get_public_stats.return_value = NotePublicStatsCollection(
            values=[
                NotePublicStats(
                    note_id=note.id,
                    view_count=9,
                    reaction_counts=NoteReactionCounts(
                        heart=2,
                        fire=1,
                        thinking=3,
                        neutral=4,
                        poop=5,
                    ),
                ),
            ],
        )

        response = self.api.get_note(slug="detail-note", only_published=False)

        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "id": str(note.id),
            "title": "Detail note",
            "slug": "detail-note",
            "folder": "General",
            "authorUsername": "admin",
            "publishedAt": "2026-01-02T03:04:05+00:00",
            "publishStatus": "Published",
            "updatedAt": "2026-01-03T03:04:05+00:00",
            "excerpt": "Markdown detail",
            "viewCount": 9,
            "tags": [
                {
                    "id": 2,
                    "name": "Old",
                    "slug": "old",
                    "deletedAt": "2026-01-04T03:04:05+00:00",
                },
            ],
            "content": "# Markdown detail",
            "createdAt": "2026-01-01T03:04:05+00:00",
            "reactionCounts": {
                "heart": 2,
                "fire": 1,
                "thinking": 3,
                "neutral": 4,
                "poop": 5,
            },
        }
        self.use_case.get_note.assert_called_once_with(slug="detail-note", only_published=False)
        self.analytics_use_case.track_public_view.assert_not_called()

    def test_public_get_note_tracks_view(self) -> None:
        note = self.factory.core.note(
            note_id=uuid.UUID(int=2),
            title="Public note",
            slug="public-note",
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        self.use_case.get_note.return_value = note
        self.analytics_use_case.get_public_stats.return_value = NotePublicStatsCollection(
            values=[
                NotePublicStats(
                    note_id=note.id,
                    view_count=1,
                    reaction_counts=NoteReactionCounts(
                        heart=0,
                        fire=0,
                        thinking=0,
                        neutral=0,
                        poop=0,
                    ),
                ),
            ],
        )

        response = self.no_auth_api.get_note(slug="public-note")

        assert response.status_code == codes.OK, response.content
        assert response.json()["viewCount"] == 1
        self.analytics_use_case.track_public_view.assert_called_once_with(
            note=note,
            referrer=None,
        )

    def test_get_note_not_found(self) -> None:
        self.use_case.get_note.side_effect = NoteNotFoundError()

        response = self.api.get_note(slug="missing")

        assert response.status_code == codes.NOT_FOUND
        assert response.json()["message"] == NoteNotFoundError.message

    def test_anonymous_cannot_request_draft_note(self) -> None:
        response = self.no_auth_api.get_note(slug="draft", only_published=False)

        assert response.status_code == codes.FORBIDDEN
        assert response.json()["message"] == ForbiddenError.message
        self.use_case.get_note.assert_not_called()

    def test_tree_uses_public_visibility_for_anonymous_users(self) -> None:
        self.use_case.list_tree.return_value = NoteTree(
            folders=[
                NoteTreeFolder(
                    folder="Engineering",
                    notes=[
                        NoteTreeItem(
                            title="Public note",
                            slug="public-note",
                            publish_status=PublishStatusEnum.PUBLISHED,
                            published_at=datetime.fromisoformat("2026-01-02T03:04:05").replace(
                                tzinfo=UTC,
                            ),
                            updated_at=datetime.fromisoformat("2026-01-03T03:04:05").replace(
                                tzinfo=UTC,
                            ),
                        ),
                    ],
                ),
            ],
        )

        response = self.no_auth_api.get_notes_tree()

        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "folders": [
                {
                    "folder": "Engineering",
                    "notes": [
                        {
                            "title": "Public note",
                            "slug": "public-note",
                            "publishStatus": "Published",
                            "publishedAt": "2026-01-02T03:04:05+00:00",
                            "updatedAt": "2026-01-03T03:04:05+00:00",
                        },
                    ],
                },
            ],
        }
        self.use_case.list_tree.assert_called_once_with(only_published=True)
