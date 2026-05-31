import uuid
from datetime import date

import pytest_asyncio
from httpx import codes

from core.i18n.enums import LanguageEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from core.notes.schemas import (
    NoteAnalyticsDailyStats,
    NoteAnalyticsNoteStats,
    NoteAnalyticsStats,
    NoteAnalyticsTotals,
    NoteReactionCounts,
)
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestNoteAnalyticsAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.analytics_use_case = await self.container.get_note_analytics_use_case()

    def test_track_engaged_view(self) -> None:
        response = self.no_auth_api.post_note_engaged_view(slug="public-note")

        assert response.status_code == codes.NO_CONTENT, response.content
        self.analytics_use_case.track_engaged_view.assert_called_once_with(
            slug="public-note",
            source_category=NoteViewSourceCategory.UNKNOWN,
        )

    def test_set_reaction(self) -> None:
        response = self.no_auth_api.post_note_reaction(
            slug="public-note",
            data={"reactionKind": "heart", "clientToken": "client-token"},
        )

        assert response.status_code == codes.NO_CONTENT, response.content
        self.analytics_use_case.set_reaction.assert_called_once_with(
            slug="public-note",
            client_token="client-token",  # noqa: S106
            reaction_kind=NoteReactionKind.HEART,
        )

    def test_clear_reaction(self) -> None:
        response = self.no_auth_api.post_note_reaction(
            slug="public-note",
            data={"reactionKind": None, "clientToken": "client-token"},
        )

        assert response.status_code == codes.NO_CONTENT, response.content
        self.analytics_use_case.set_reaction.assert_called_once_with(
            slug="public-note",
            client_token="client-token",  # noqa: S106
            reaction_kind=None,
        )

    def test_get_stats_requires_admin(self) -> None:
        response = self.no_auth_api.get_note_stats(date_from="2026-01-01", date_to="2026-01-31")

        assert response.status_code == codes.UNAUTHORIZED
        self.analytics_use_case.get_stats.assert_not_called()

    def test_get_stats(self) -> None:
        note_id = uuid.UUID(int=1)
        self.analytics_use_case.get_stats.return_value = NoteAnalyticsStats(
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 31),
            totals=NoteAnalyticsTotals(
                view_count=7,
                engaged_view_count=3,
                reaction_count=2,
            ),
            notes=[
                NoteAnalyticsNoteStats(
                    note_id=note_id,
                    title="Typed notes",
                    slug="typed-notes",
                    view_count=7,
                    engaged_view_count=3,
                    reaction_counts=NoteReactionCounts(
                        heart=1,
                        fire=0,
                        thinking=1,
                        neutral=0,
                        poop=0,
                    ),
                ),
            ],
            daily=[
                NoteAnalyticsDailyStats(
                    note_id=note_id,
                    title="Typed notes",
                    slug="typed-notes",
                    date=date(2026, 1, 2),
                    source_category=NoteViewSourceCategory.SEARCH,
                    view_count=7,
                    engaged_view_count=3,
                ),
            ],
        )

        response = self.api.get_note_stats(date_from="2026-01-01", date_to="2026-01-31")

        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "dateFrom": "2026-01-01",
            "dateTo": "2026-01-31",
            "totals": {
                "viewCount": 7,
                "engagedViewCount": 3,
                "reactionCount": 2,
            },
            "notes": [
                {
                    "noteId": str(note_id),
                    "title": "Typed notes",
                    "slug": "typed-notes",
                    "viewCount": 7,
                    "engagedViewCount": 3,
                    "reactionCounts": {
                        "heart": 1,
                        "fire": 0,
                        "thinking": 1,
                        "neutral": 0,
                        "poop": 0,
                    },
                },
            ],
            "daily": [
                {
                    "noteId": str(note_id),
                    "title": "Typed notes",
                    "slug": "typed-notes",
                    "date": "2026-01-02",
                    "sourceCategory": "Search",
                    "viewCount": 7,
                    "engagedViewCount": 3,
                },
            ],
        }
        self.analytics_use_case.get_stats.assert_called_once_with(
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 31),
            language=LanguageEnum.RU,
        )
