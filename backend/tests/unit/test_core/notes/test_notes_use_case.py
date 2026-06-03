import uuid
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.notes.exceptions import NoteNotFoundError, TagNotFoundError
from core.notes.schemas import (
    NoteCreateParams,
    NoteFilters,
    NoteMetadata,
    NoteTreeItemData,
    NoteUpdateParams,
    PublishedNoteForSeo,
    PublishedNotesForSeo,
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

    async def test_list_notes_builds_page_from_storage_rows(self) -> None:
        filters = NoteFilters(
            page=1,
            page_size=10,
            language=LanguageEnum.RU,
            only_published=True,
            tag_slug="python",
            published_from=None,
            published_to=None,
            search_query=None,
            include_tags=True,
        )
        note = self.factory.core.note(title="Published note", slug="published-note")
        self.storage.list_notes.return_value = ([note], 11)

        result = await self.use_case.list_notes(filters=filters)

        assert result.values == [note]
        assert result.total_count == 11
        assert result.total_pages == 2
        self.storage.list_notes.assert_called_once_with(filters=filters)

    async def test_list_notes_requires_pagination_before_storage_call(self) -> None:
        with pytest.raises(ValueError, match="pagination required"):
            await self.use_case.list_notes(filters=NoteFilters())

        self.storage.list_notes.assert_not_called()

    async def test_list_published_notes_for_seo_uses_shared_storage_list_and_available_notes(
        self,
    ) -> None:
        first_updated_at = datetime(2026, 1, 1, tzinfo=UTC)
        first_note = self.factory.core.note(
            title="First note",
            slug="first-note",
            publish_status=PublishStatusEnum.PUBLISHED,
            updated_at="2026-01-01T00:00:00",
        )
        draft_note = self.factory.core.note(
            title="Draft note",
            slug="draft-note",
            publish_status=PublishStatusEnum.DRAFT,
            updated_at="2026-01-02T00:00:00",
        )
        self.storage.list_notes.return_value = ([first_note, draft_note], 2)

        result = await self.use_case.list_published_notes_for_seo()

        assert result == PublishedNotesForSeo(
            values=[
                PublishedNoteForSeo(
                    slug="first-note",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    updated_at=first_updated_at,
                ),
            ],
        )
        self.storage.list_notes.assert_called_once_with(
            filters=NoteFilters(only_published=True, include_tags=False, order_for_seo=True),
        )

    async def test_list_tree_builds_folders_from_storage_items(self) -> None:
        first_updated_at = datetime(2026, 1, 1, tzinfo=UTC)
        second_updated_at = datetime(2026, 1, 2, tzinfo=UTC)
        self.storage.list_tree_items.return_value = [
            NoteTreeItemData(
                folder="Backend",
                title="Storage",
                slug="storage",
                publish_status=PublishStatusEnum.PUBLISHED,
                published_at=datetime(2026, 1, 1, tzinfo=UTC),
                updated_at=first_updated_at,
            ),
            NoteTreeItemData(
                folder="Architecture",
                title="Boundaries",
                slug="boundaries",
                publish_status=PublishStatusEnum.DRAFT,
                published_at=None,
                updated_at=second_updated_at,
            ),
        ]

        result = await self.use_case.list_tree(
            only_published=False,
            language=LanguageEnum.EN,
        )

        assert [folder.folder for folder in result.folders] == ["Architecture", "Backend"]
        assert [item.slug for item in result.folders[0].notes] == ["boundaries"]
        assert [item.slug for item in result.folders[1].notes] == ["storage"]
        self.storage.list_tree_items.assert_called_once_with(
            only_published=False,
            language=LanguageEnum.EN,
        )

    async def test_get_note_rejects_draft_when_only_published(self) -> None:
        self.storage.get_note_by_slug.return_value = self.factory.core.note(
            slug="draft-note",
            publish_status=PublishStatusEnum.DRAFT,
        )

        with pytest.raises(NoteNotFoundError):
            await self.use_case.get_note(
                slug="draft-note",
                only_published=True,
            )

    async def test_get_note_returns_draft_when_admin_requests_all_notes(self) -> None:
        expected = self.factory.core.note(
            slug="draft-note",
            publish_status=PublishStatusEnum.DRAFT,
        )
        self.storage.get_note_by_slug.return_value = expected

        result = await self.use_case.get_note(
            slug="draft-note",
            only_published=False,
        )

        assert result == expected
        self.storage.get_note_by_slug.assert_called_once_with(
            slug="draft-note",
            include_deleted_tags=True,
        )

    async def test_create_note_requires_all_tags_to_exist_and_be_active(self) -> None:
        tag_ids = [IntId(1), IntId(2)]
        params = NoteCreateParams(
            id=uuid.uuid4(),
            slug="note",
            title_ru="Заметка",
            title_en="Note",
            content_ru="Содержимое",
            content_en="Content",
            folder_ru="Питон",
            folder_en="Python",
            author_username="admin",
            publish_status=PublishStatusEnum.DRAFT,
            metadata=NoteMetadata(
                seo_title_ru=None,
                seo_title_en=None,
                seo_description_ru=None,
                seo_description_en=None,
                cover_image_url=None,
                cover_image_alt_ru=None,
                cover_image_alt_en=None,
            ),
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
        params = NoteCreateParams(
            id=note_id,
            slug="note",
            title_ru="Заметка",
            title_en="Note",
            content_ru="Содержимое",
            content_en="Content",
            folder_ru="Питон",
            folder_en="Python",
            author_username="admin",
            publish_status=PublishStatusEnum.DRAFT,
            metadata=NoteMetadata(
                seo_title_ru="SEO заметка",
                seo_title_en="SEO note",
                seo_description_ru="Описание для поиска",
                seo_description_en="Search description",
                cover_image_url="https://example.com/cover.jpg",
                cover_image_alt_ru="Обложка",
                cover_image_alt_en="Cover",
            ),
            tag_ids=tag_ids,
        )
        tag = self.factory.core.tag(tag_id=IntId(1), slug="python")
        expected = self.factory.core.note(
            note_id=note_id,
            slug="note",
            title_ru="Заметка",
            title_en="Note",
            content_ru="Содержимое",
            content_en="Content",
            folder_ru="Питон",
            folder_en="Python",
            author_username="admin",
            publish_status=PublishStatusEnum.DRAFT,
            metadata=NoteMetadata(
                seo_title_ru="SEO заметка",
                seo_title_en="SEO note",
                seo_description_ru="Описание для поиска",
                seo_description_en="Search description",
                cover_image_url="https://example.com/cover.jpg",
                cover_image_alt_ru="Обложка",
                cover_image_alt_en="Cover",
            ),
            tags=[tag],
        )
        self.storage.get_tags_by_ids.return_value = self.factory.core.tags(values=[tag])
        self.storage.create_note.return_value = expected

        result = await self.use_case.create_note(params=params)

        assert result == expected
        self.storage.create_note.assert_called_once()
        created_note = self.storage.create_note.call_args.kwargs["note"]
        assert not hasattr(created_note, "title")
        assert not hasattr(created_note, "content")
        assert not hasattr(created_note, "folder")
        assert created_note.localized_title(language=LanguageEnum.RU) == "Заметка"
        assert created_note.localized_content(language=LanguageEnum.RU) == "Содержимое"
        assert created_note.localized_folder(language=LanguageEnum.RU) == "Питон"
        assert created_note.title_ru == "Заметка"
        assert created_note.title_en == "Note"
        assert created_note.metadata == params.metadata
        assert created_note.author_username == "admin"
        assert created_note.tags.values == [tag]

    def test_note_create_params_builds_canonical_note(self) -> None:
        note_id = uuid.uuid4()
        now = datetime(2026, 5, 31, 12, 0, tzinfo=UTC)
        tag = self.factory.core.tag(tag_id=IntId(1), slug="python")
        params = NoteCreateParams(
            id=note_id,
            slug="note",
            title_ru="Заметка",
            title_en="Note",
            content_ru="Содержимое",
            content_en="Content",
            folder_ru="Питон",
            folder_en="Python",
            author_username="admin",
            publish_status=PublishStatusEnum.PUBLISHED,
            metadata=NoteMetadata(
                seo_title_ru=None,
                seo_title_en=None,
                seo_description_ru=None,
                seo_description_en=None,
                cover_image_url=None,
                cover_image_alt_ru=None,
                cover_image_alt_en=None,
            ),
            tag_ids=[IntId(1)],
        )

        note = params.to_note(now=now, tags=self.factory.core.tags(values=[tag]))

        assert not hasattr(note, "title")
        assert not hasattr(note, "content")
        assert not hasattr(note, "folder")
        assert note.localized_title(language=LanguageEnum.RU) == "Заметка"
        assert note.localized_title(language=LanguageEnum.EN) == "Note"
        assert note.metadata == params.metadata
        assert note.published_at == now
        assert note.created_at == now
        assert note.updated_at == now
        assert note.tags.values == [tag]

    async def test_update_note_keeps_existing_author(self) -> None:
        tag = self.factory.core.tag(tag_id=IntId(1), slug="python")
        existing = self.factory.core.note(
            slug="old-note",
            author_username="original-author",
            tags=[tag],
        )
        params = NoteUpdateParams(
            slug="new-note",
            title_ru="Новая",
            title_en="New",
            content_ru="Новый контент",
            content_en="New content",
            folder_ru="Архитектура",
            folder_en="Architecture",
            publish_status=PublishStatusEnum.PUBLISHED,
            metadata=NoteMetadata(
                seo_title_ru="Новая SEO",
                seo_title_en="New SEO",
                seo_description_ru="Новое описание",
                seo_description_en="New description",
                cover_image_url=None,
                cover_image_alt_ru=None,
                cover_image_alt_en=None,
            ),
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

        await self.use_case.update_note(
            slug="old-note",
            params=params,
        )

        updated_note = self.storage.update_note.call_args.kwargs["note"]
        assert updated_note.id == existing.id
        assert updated_note.author_username == "original-author"
        assert updated_note.title_ru == "Новая"
        assert updated_note.title_en == "New"
        assert updated_note.metadata == params.metadata
        assert not hasattr(updated_note, "title")

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
        params = TagCreateParams(
            id=IntId(1),
            name_ru="Питон",
            name_en="Python",
            slug="python",
        )
        expected = self.factory.core.tag(
            tag_id=IntId(1),
            name_ru="Питон",
            name_en="Python",
            slug="python",
        )
        self.storage.create_tag.return_value = expected

        result = await self.use_case.create_tag(params=params)

        assert result == expected
        self.storage.create_tag.assert_called_once_with(tag=expected)

    async def test_update_tag_delegates_to_storage(self) -> None:
        params = TagUpdateParams(
            name_ru="Питон обновлённый",
            name_en="Python Updated",
            slug="python-updated",
        )
        expected = self.factory.core.tag(
            tag_id=IntId(1),
            name_ru="Питон обновлённый",
            name_en="Python Updated",
            slug="python-updated",
        )
        self.storage.update_tag.return_value = expected

        result = await self.use_case.update_tag(
            tag_id=IntId(1),
            params=params,
        )

        assert result == expected
        self.storage.update_tag.assert_called_once_with(tag=expected)
