import uuid
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from core.enums import PublishStatusEnum
from core.notes.exceptions import NoteNotFoundError, TagNotFoundError
from core.notes.schemas import (
    NoteCreateParams,
    NoteFilters,
    NoteUpdateParams,
    TagCreateParams,
    TagUpdateParams,
)
from core.notes.storages import NotesStorage
from core.notes.use_cases import NotesUseCase
from core.types import IntId
from tests.unit.fixtures import FactoryFixture


class TestNotesUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=NotesStorage)
        self.use_case = NotesUseCase(storage=self.storage)

    async def test_list_notes_delegates_filters_to_storage(self) -> None:
        filters = NoteFilters(page=1, page_size=10, only_published=True, tag_slug="python")
        expected = self.factory.core.note_list(
            notes=[self.factory.core.note(title="Published note", slug="published-note")],
            total_count=1,
            total_pages=1,
        )
        self.storage.list_notes.return_value = expected

        result = await self.use_case.list_notes(filters=filters)

        assert result == expected
        self.storage.list_notes.assert_called_once_with(filters=filters)

    async def test_get_note_rejects_draft_when_only_published(self) -> None:
        self.storage.get_note_by_slug.return_value = self.factory.core.note(
            slug="draft-note",
            publish_status=PublishStatusEnum.DRAFT,
        )

        with pytest.raises(NoteNotFoundError):
            await self.use_case.get_note(slug="draft-note", only_published=True)

    async def test_get_note_returns_draft_when_admin_requests_all_notes(self) -> None:
        expected = self.factory.core.note(
            slug="draft-note",
            publish_status=PublishStatusEnum.DRAFT,
        )
        self.storage.get_note_by_slug.return_value = expected

        result = await self.use_case.get_note(slug="draft-note", only_published=False)

        assert result == expected
        self.storage.get_note_by_slug.assert_called_once_with(
            slug="draft-note",
            include_deleted_tags=True,
        )

    async def test_create_note_requires_all_tags_to_exist_and_be_active(self) -> None:
        tag_ids = [IntId(1), IntId(2)]
        params = NoteCreateParams(
            id=uuid.uuid4(),
            title="Note",
            content="Content",
            slug="note",
            folder="Python",
            author_username="admin",
            publish_status=PublishStatusEnum.DRAFT,
            tag_ids=tag_ids,
        )
        self.storage.get_tags_by_ids.return_value = self.factory.core.tags(
            values=[self.factory.core.tag(tag_id=IntId(1))],
        )

        with pytest.raises(TagNotFoundError):
            await self.use_case.create_note(params=params)

    async def test_create_note_persists_note_with_active_tags(self) -> None:
        tag_ids = [IntId(1)]
        note_id = uuid.uuid4()
        now = datetime.now(tz=UTC)
        params = NoteCreateParams(
            id=note_id,
            title="Note",
            content="Content",
            slug="note",
            folder="Python",
            author_username="admin",
            publish_status=PublishStatusEnum.DRAFT,
            tag_ids=tag_ids,
        )
        tag = self.factory.core.tag(tag_id=IntId(1), slug="python")
        expected = self.factory.core.note(
            note_id=note_id,
            title="Note",
            content="Content",
            slug="note",
            folder="Python",
            author_username="admin",
            publish_status=PublishStatusEnum.DRAFT,
            tags=[tag],
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
        )
        self.storage.get_tags_by_ids.return_value = self.factory.core.tags(values=[tag])
        self.storage.create_note.return_value = expected

        result = await self.use_case.create_note(params=params)

        assert result == expected
        self.storage.create_note.assert_called_once()
        created_note = self.storage.create_note.call_args.kwargs["note"]
        assert created_note.title == "Note"
        assert created_note.author_username == "admin"
        assert created_note.tags.values == [tag]

    async def test_update_note_keeps_existing_author(self) -> None:
        tag = self.factory.core.tag(tag_id=IntId(1), slug="python")
        existing = self.factory.core.note(
            slug="old-note",
            author_username="original-author",
            tags=[tag],
        )
        params = NoteUpdateParams(
            title="New",
            content="New content",
            slug="new-note",
            folder="Architecture",
            publish_status=PublishStatusEnum.PUBLISHED,
            tag_ids=[IntId(1)],
        )
        self.storage.get_note_by_slug.return_value = existing
        self.storage.get_tags_by_ids.return_value = self.factory.core.tags(values=[tag])
        self.storage.update_note.return_value = self.factory.core.note(
            title="New",
            slug="new-note",
            author_username="original-author",
            publish_status=PublishStatusEnum.PUBLISHED,
            tags=[tag],
        )

        await self.use_case.update_note(slug="old-note", params=params)

        updated_note = self.storage.update_note.call_args.kwargs["note"]
        assert updated_note.id == existing.id
        assert updated_note.author_username == "original-author"
        assert updated_note.title == "New"

    async def test_switch_publish_status_delegates_to_storage(self) -> None:
        await self.use_case.switch_note_publish_status(
            slug="note",
            publish_status=PublishStatusEnum.PUBLISHED,
        )

        self.storage.update_note_publish_status.assert_called_once_with(
            slug="note",
            publish_status=PublishStatusEnum.PUBLISHED,
        )

    async def test_create_tag_delegates_to_storage(self) -> None:
        params = TagCreateParams(id=IntId(1), name="Python", slug="python")
        expected = self.factory.core.tag(tag_id=IntId(1), name="Python", slug="python")
        self.storage.create_tag.return_value = expected

        result = await self.use_case.create_tag(params=params)

        assert result == expected
        self.storage.create_tag.assert_called_once_with(tag=expected)

    async def test_update_tag_delegates_to_storage(self) -> None:
        params = TagUpdateParams(name="Python Updated", slug="python-updated")
        expected = self.factory.core.tag(
            tag_id=IntId(1),
            name="Python Updated",
            slug="python-updated",
        )
        self.storage.update_tag.return_value = expected

        result = await self.use_case.update_tag(tag_id=IntId(1), params=params)

        assert result == expected
        self.storage.update_tag.assert_called_once_with(tag=expected)
