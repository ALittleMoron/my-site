import uuid

import pytest_asyncio
from httpx import codes

from core.enums import PublishStatusEnum
from core.notes.exceptions import NoteNotFoundError
from core.notes.schemas import NoteCreateParams, NoteUpdateParams
from core.types import IntId
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestAdminNotesAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.note_id = await self.container.get_random_uuid()
        self.use_case = await self.container.get_notes_use_case()

    def test_create_note_saves_author(self) -> None:
        note = self.factory.core.note(
            note_id=self.note_id,
            title="New note",
            content="New content",
            slug="new-note",
            folder="Inbox",
            author_username="test",
            publish_status=PublishStatusEnum.DRAFT,
            created_at="2026-01-01T03:04:05",
            updated_at="2026-01-01T03:04:05",
        )
        self.use_case.create_note.return_value = note

        response = self.api.post_create_note(
            data=self.factory.api.note_request(
                title="New note",
                content="New content",
                slug="new-note",
                folder="Inbox",
                publish_status="Draft",
                tag_ids=[IntId(1), IntId(2)],
            ),
        )

        assert response.status_code == codes.CREATED, response.content
        assert response.json()["authorUsername"] == "test"
        self.use_case.create_note.assert_called_once_with(
            params=NoteCreateParams(
                id=self.note_id,
                title="New note",
                content="New content",
                slug="new-note",
                folder="Inbox",
                author_username="test",
                publish_status=PublishStatusEnum.DRAFT,
                tag_ids=[IntId(1), IntId(2)],
            ),
        )

    def test_update_note(self) -> None:
        note = self.factory.core.note(
            note_id=uuid.UUID(int=1),
            title="Updated note",
            content="Updated content",
            slug="updated-note",
            folder="Inbox",
            author_username="test",
            publish_status=PublishStatusEnum.PUBLISHED,
            published_at="2026-01-02T03:04:05",
            created_at="2026-01-01T03:04:05",
            updated_at="2026-01-03T03:04:05",
        )
        self.use_case.update_note.return_value = note

        response = self.api.put_update_note(
            slug="old-note",
            data=self.factory.api.note_request(
                title="Updated note",
                content="Updated content",
                slug="updated-note",
                folder="Inbox",
                publish_status="Published",
                tag_ids=[IntId(1)],
            ),
        )

        assert response.status_code == codes.OK, response.content
        assert response.json()["slug"] == "updated-note"
        self.use_case.update_note.assert_called_once_with(
            slug="old-note",
            params=NoteUpdateParams(
                title="Updated note",
                content="Updated content",
                slug="updated-note",
                folder="Inbox",
                publish_status=PublishStatusEnum.PUBLISHED,
                tag_ids=[IntId(1)],
            ),
        )

    def test_delete_note_not_found(self) -> None:
        self.use_case.delete_note.side_effect = NoteNotFoundError()

        response = self.api.delete_note(slug="missing")

        assert response.status_code == codes.NOT_FOUND
        assert response.json()["message"] == NoteNotFoundError.message

    def test_delete_note(self) -> None:
        response = self.api.delete_note(slug="old-note")

        assert response.status_code == codes.NO_CONTENT
        self.use_case.delete_note.assert_called_once_with(slug="old-note")

    def test_set_published_status_to_note(self) -> None:
        response = self.api.post_set_published_status_to_note(slug="draft-note")

        assert response.status_code == codes.NO_CONTENT
        self.use_case.switch_note_publish_status.assert_called_once_with(
            slug="draft-note",
            publish_status=PublishStatusEnum.PUBLISHED,
        )

    def test_set_draft_status_to_note(self) -> None:
        response = self.api.post_set_draft_status_to_note(slug="published-note")

        assert response.status_code == codes.NO_CONTENT
        self.use_case.switch_note_publish_status.assert_called_once_with(
            slug="published-note",
            publish_status=PublishStatusEnum.DRAFT,
        )
