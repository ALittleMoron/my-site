import uuid
from datetime import date
from unittest.mock import Mock

import pytest

from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from core.notes.exceptions import NoteNotFoundError
from core.notes.schemas import (
    NoteAnalyticsDailyStats,
    NotePublicStatsCollection,
    NoteReactionCounts,
)
from core.notes.storages import NoteAnalyticsStorage, NotesStorage
from core.notes.use_cases import NoteAnalyticsUseCase
from core.schemas import Secret
from tests.fixtures import FactoryFixture


class TestNoteAnalyticsUseCase(FactoryFixture):
    def setup_method(self) -> None:
        self.notes_storage = Mock(spec=NotesStorage)
        self.analytics_storage = Mock(spec=NoteAnalyticsStorage)
        self.error_reporter = Mock()
        self.use_case = NoteAnalyticsUseCase(
            notes_storage=self.notes_storage,
            analytics_storage=self.analytics_storage,
            reaction_secret=Secret("reaction-secret"),
            app_domain="example.com",
            error_reporter=self.error_reporter,
        )

    async def test_track_view_delegates_published_note(self) -> None:
        note = self.factory.core.note(
            note_id=uuid.UUID(int=1),
            publish_status=PublishStatusEnum.PUBLISHED,
        )

        await self.use_case.track_view(
            note=note,
            source_category=NoteViewSourceCategory.SEARCH,
        )

        self.analytics_storage.increment_view.assert_called_once_with(
            note_id=note.id,
            source_category=NoteViewSourceCategory.SEARCH,
            viewed_on=None,
        )

    async def test_track_view_ignores_draft_note(self) -> None:
        note = self.factory.core.note(
            note_id=uuid.UUID(int=1),
            publish_status=PublishStatusEnum.DRAFT,
        )

        await self.use_case.track_view(
            note=note,
            source_category=NoteViewSourceCategory.SEARCH,
        )

        self.analytics_storage.increment_view.assert_not_called()

    async def test_track_public_view_classifies_referrer(self) -> None:
        note = self.factory.core.note(
            note_id=uuid.UUID(int=1),
            publish_status=PublishStatusEnum.PUBLISHED,
        )

        await self.use_case.track_public_view(
            note=note,
            referrer="https://www.google.com/search?q=typed",
        )

        self.analytics_storage.increment_view.assert_called_once_with(
            note_id=note.id,
            source_category=NoteViewSourceCategory.SEARCH,
            viewed_on=None,
        )

    async def test_track_public_view_reports_error_without_raising(self) -> None:
        note = self.factory.core.note(
            note_id=uuid.UUID(int=1),
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        error = RuntimeError("db is down")
        self.analytics_storage.increment_view.side_effect = error

        await self.use_case.track_public_view(note=note, referrer=None)

        self.error_reporter.report_public_view_tracking_failure.assert_called_once_with(
            note=note,
            error=error,
        )

    async def test_track_engaged_view_rejects_draft_note(self) -> None:
        self.notes_storage.get_note_by_slug.return_value = self.factory.core.note(
            publish_status=PublishStatusEnum.DRAFT,
        )

        with pytest.raises(NoteNotFoundError):
            await self.use_case.track_engaged_view(
                slug="draft-note",
                source_category=NoteViewSourceCategory.UNKNOWN,
            )

        self.analytics_storage.increment_engaged_view.assert_not_called()

    async def test_same_token_is_note_scoped_for_reactions(self) -> None:
        first_note = self.factory.core.note(note_id=uuid.UUID(int=1), slug="first")
        second_note = self.factory.core.note(note_id=uuid.UUID(int=2), slug="second")
        self.notes_storage.get_note_by_slug.side_effect = [first_note, second_note]

        await self.use_case.set_reaction(
            slug="first",
            client_token="same-client-token",  # noqa: S106
            reaction_kind=NoteReactionKind.HEART,
        )
        await self.use_case.set_reaction(
            slug="second",
            client_token="same-client-token",  # noqa: S106
            reaction_kind=NoteReactionKind.HEART,
        )

        first_call, second_call = self.analytics_storage.set_reaction.call_args_list
        assert first_call.kwargs["note_id"] == first_note.id
        assert second_call.kwargs["note_id"] == second_note.id
        assert (
            first_call.kwargs["note_scoped_voter_hash"]
            != second_call.kwargs["note_scoped_voter_hash"]
        )

    async def test_public_stats_are_filled_with_zero_counts(self) -> None:
        note_id = uuid.UUID(int=1)
        self.analytics_storage.get_public_stats.return_value = NotePublicStatsCollection(
            values=[],
        )

        result = await self.use_case.get_public_stats(note_ids=[note_id])

        assert result.values[0].note_id == note_id
        assert result.values[0].view_count == 0
        assert result.values[0].reaction_counts == NoteReactionCounts(
            heart=0,
            fire=0,
            thinking=0,
            neutral=0,
            poop=0,
        )

    async def test_get_stats_builds_totals_and_note_rows_from_storage_data(self) -> None:
        note_id = uuid.UUID(int=1)
        self.analytics_storage.get_daily_stats.return_value = [
            NoteAnalyticsDailyStats(
                note_id=note_id,
                title="Typed notes",
                slug="typed-notes",
                date=date(2026, 1, 2),
                source_category=NoteViewSourceCategory.SEARCH,
                view_count=4,
                engaged_view_count=1,
            ),
            NoteAnalyticsDailyStats(
                note_id=note_id,
                title="Typed notes",
                slug="typed-notes",
                date=date(2026, 1, 3),
                source_category=NoteViewSourceCategory.DIRECT,
                view_count=3,
                engaged_view_count=2,
            ),
        ]
        self.analytics_storage.get_reaction_counts.return_value = {
            note_id: NoteReactionCounts(
                heart=1,
                fire=0,
                thinking=1,
                neutral=0,
                poop=0,
            ),
        }

        result = await self.use_case.get_stats(
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 31),
            language=LanguageEnum.RU,
        )

        assert result.totals.view_count == 7
        assert result.totals.engaged_view_count == 3
        assert result.totals.reaction_count == 2
        assert len(result.notes) == 1
        assert result.notes[0].note_id == note_id
        assert result.notes[0].view_count == 7
        assert result.notes[0].engaged_view_count == 3
        assert result.notes[0].reaction_counts.thinking == 1
        assert result.daily == self.analytics_storage.get_daily_stats.return_value
        self.analytics_storage.get_daily_stats.assert_called_once_with(
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 31),
            language=LanguageEnum.RU,
        )
        self.analytics_storage.get_reaction_counts.assert_called_once_with(note_ids=[note_id])
