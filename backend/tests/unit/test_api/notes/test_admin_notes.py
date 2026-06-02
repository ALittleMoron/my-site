import uuid

import pytest
import pytest_asyncio
from httpx import codes

from core.enums import PublishStatusEnum
from core.notes.exceptions import NoteNotFoundError
from core.notes.schemas import NoteCreateParams, NoteUpdateParams
from core.types import IntId
from entrypoints.litestar.response_cache import ResponseCacheDomain
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
                title_ru="Новая заметка",
                title_en="New note",
                content_ru="Новое содержимое",
                content_en="New content",
                slug="new-note",
                folder_ru="Входящие",
                folder_en="Inbox",
                publish_status="Draft",
                tag_ids=[IntId(1), IntId(2)],
            ),
        )

        assert response.status_code == codes.CREATED, response.content
        assert response.json()["authorUsername"] == "test"
        self.use_case.create_note.assert_called_once_with(
            params=NoteCreateParams(
                id=self.note_id,
                slug="new-note",
                title_ru="Новая заметка",
                title_en="New note",
                content_ru="Новое содержимое",
                content_en="New content",
                folder_ru="Входящие",
                folder_en="Inbox",
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
                title_ru="Обновлённая заметка",
                title_en="Updated note",
                content_ru="Обновлённое содержимое",
                content_en="Updated content",
                slug="updated-note",
                folder_ru="Входящие",
                folder_en="Inbox",
                publish_status="Published",
                tag_ids=[IntId(1)],
            ),
        )

        assert response.status_code == codes.OK, response.content
        assert response.json()["slug"] == "updated-note"
        self.use_case.update_note.assert_called_once_with(
            slug="old-note",
            params=NoteUpdateParams(
                slug="updated-note",
                title_ru="Обновлённая заметка",
                title_en="Updated note",
                content_ru="Обновлённое содержимое",
                content_en="Updated content",
                folder_ru="Входящие",
                folder_en="Inbox",
                publish_status=PublishStatusEnum.PUBLISHED,
                tag_ids=[IntId(1)],
            ),
        )

    def test_create_note_requires_all_translation_fields(self) -> None:
        data = self.factory.api.note_request()
        del data["translations"]["en"]["content"]

        response = self.api.post_create_note(data=data)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.create_note.assert_not_called()

    def test_create_note_validation_error_does_not_invalidate_response_cache(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        invalidated_domains: list[ResponseCacheDomain] = []

        async def fake_invalidate_response_cache_domain(
            *,
            request: object,
            domain: ResponseCacheDomain,
        ) -> None:
            _ = request
            invalidated_domains.append(domain)

        monkeypatch.setattr(
            "entrypoints.litestar.api.notes.endpoints.invalidate_response_cache_domain",
            fake_invalidate_response_cache_domain,
            raising=False,
        )
        data = self.factory.api.note_request()
        del data["translations"]["en"]["content"]

        response = self.api.post_create_note(data=data)

        assert response.status_code == codes.BAD_REQUEST
        assert invalidated_domains == []

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

    def test_successful_note_mutations_invalidate_notes_response_cache(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        invalidated_domains: list[ResponseCacheDomain] = []

        async def fake_invalidate_response_cache_domain(
            *,
            request: object,
            domain: ResponseCacheDomain,
        ) -> None:
            _ = request
            invalidated_domains.append(domain)

        monkeypatch.setattr(
            "entrypoints.litestar.api.notes.endpoints.invalidate_response_cache_domain",
            fake_invalidate_response_cache_domain,
            raising=False,
        )
        created_note = self.factory.core.note(
            note_id=self.note_id,
            slug="new-note",
            publish_status=PublishStatusEnum.DRAFT,
        )
        updated_note = self.factory.core.note(
            note_id=uuid.UUID(int=1),
            slug="updated-note",
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        self.use_case.create_note.return_value = created_note
        self.use_case.update_note.return_value = updated_note

        responses = [
            self.api.post_create_note(data=self.factory.api.note_request(slug="new-note")),
            self.api.put_update_note(
                slug="old-note",
                data=self.factory.api.note_request(slug="updated-note"),
            ),
            self.api.delete_note(slug="updated-note"),
            self.api.post_set_published_status_to_note(slug="draft-note"),
            self.api.post_set_draft_status_to_note(slug="published-note"),
        ]

        assert [response.status_code for response in responses] == [
            codes.CREATED,
            codes.OK,
            codes.NO_CONTENT,
            codes.NO_CONTENT,
            codes.NO_CONTENT,
        ]
        assert invalidated_domains == [ResponseCacheDomain.NOTES] * 5
