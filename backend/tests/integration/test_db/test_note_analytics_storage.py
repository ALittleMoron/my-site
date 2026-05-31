import uuid
from datetime import date

import pytest_asyncio

from core.i18n.enums import LanguageEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from infra.postgresql.storages.notes import NoteAnalyticsDatabaseStorage
from tests.fixtures import FactoryFixture, StorageFixture


class TestNoteAnalyticsDatabaseStorage(StorageFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.storage = NoteAnalyticsDatabaseStorage(session=self.db_session)

    async def test_public_stats_include_views_and_reactions(self) -> None:
        note = self.factory.core.note(note_id=uuid.UUID(int=1), slug="analytics-note")
        await self.storage_helper.create_note(note=note)

        await self.storage.increment_view(
            note_id=note.id,
            source_category=NoteViewSourceCategory.SEARCH,
            viewed_on=None,
        )
        await self.storage.increment_view(
            note_id=note.id,
            source_category=NoteViewSourceCategory.SEARCH,
            viewed_on=None,
        )
        await self.storage.increment_engaged_view(
            note_id=note.id,
            source_category=NoteViewSourceCategory.SEARCH,
            viewed_on=None,
        )
        await self.storage.set_reaction(
            note_id=note.id,
            note_scoped_voter_hash="voter-hash",
            reaction_kind=NoteReactionKind.FIRE,
        )

        result = await self.storage.get_public_stats(note_ids=[note.id])

        assert result.by_note_id(note.id).view_count == 2
        assert result.by_note_id(note.id).reaction_counts.fire == 1

    async def test_same_voter_reaction_is_replaced_and_removed(self) -> None:
        note = self.factory.core.note(note_id=uuid.UUID(int=1), slug="reaction-note")
        await self.storage_helper.create_note(note=note)

        await self.storage.set_reaction(
            note_id=note.id,
            note_scoped_voter_hash="voter-hash",
            reaction_kind=NoteReactionKind.HEART,
        )
        await self.storage.set_reaction(
            note_id=note.id,
            note_scoped_voter_hash="voter-hash",
            reaction_kind=NoteReactionKind.POOP,
        )
        replaced = await self.storage.get_public_stats(note_ids=[note.id])
        await self.storage.set_reaction(
            note_id=note.id,
            note_scoped_voter_hash="voter-hash",
            reaction_kind=None,
        )
        removed = await self.storage.get_public_stats(note_ids=[note.id])

        assert replaced.by_note_id(note.id).reaction_counts.heart == 0
        assert replaced.by_note_id(note.id).reaction_counts.poop == 1
        assert removed.by_note_id(note.id).reaction_counts.poop == 0

    async def test_stats_are_filtered_by_date_range(self) -> None:
        first_note = self.factory.core.note(note_id=uuid.UUID(int=1), slug="first")
        second_note = self.factory.core.note(note_id=uuid.UUID(int=2), slug="second")
        await self.storage_helper.create_notes(notes=[first_note, second_note])
        await self.storage.increment_view(
            note_id=first_note.id,
            source_category=NoteViewSourceCategory.EXTERNAL,
            viewed_on=date(2026, 1, 2),
        )
        await self.storage.increment_engaged_view(
            note_id=first_note.id,
            source_category=NoteViewSourceCategory.EXTERNAL,
            viewed_on=date(2026, 1, 2),
        )
        await self.storage.increment_view(
            note_id=second_note.id,
            source_category=NoteViewSourceCategory.DIRECT,
            viewed_on=date(2026, 2, 2),
        )
        await self.storage.set_reaction(
            note_id=first_note.id,
            note_scoped_voter_hash="voter-hash",
            reaction_kind=NoteReactionKind.THINKING,
        )

        daily = await self.storage.get_daily_stats(
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 31),
            language=LanguageEnum.RU,
        )
        reaction_counts = await self.storage.get_reaction_counts(note_ids=[first_note.id])

        assert [item.slug for item in daily] == ["first"]
        assert daily[0].view_count == 1
        assert daily[0].engaged_view_count == 1
        assert daily[0].source_category == NoteViewSourceCategory.EXTERNAL
        assert reaction_counts[first_note.id].thinking == 1
