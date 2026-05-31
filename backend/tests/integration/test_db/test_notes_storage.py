from datetime import date

import pytest
import pytest_asyncio

from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.notes.exceptions import NoteNotFoundError, TagNotFoundError
from core.notes.schemas import NoteFilters
from core.types import IntId
from infra.postgresql.storages.notes import NotesDatabaseStorage
from tests.fixtures import FactoryFixture, StorageFixture


class TestNotesDatabaseStorage(StorageFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.storage = NotesDatabaseStorage(session=self.db_session)

    async def test_get_note_by_slug_success(self) -> None:
        tag = self.factory.core.tag(tag_id=IntId(1), slug="python")
        deleted_tag = self.factory.core.tag(
            tag_id=IntId(2),
            name="Deleted",
            slug="deleted",
            deleted_at="2024-01-01T00:00:00",
        )
        await self.storage_helper.create_tags(tags=[tag, deleted_tag])
        await self.storage_helper.create_note(
            note=self.factory.core.note(
                title="Test Note",
                content="Test content",
                slug="test-note",
                folder="Python",
                tags=[tag, deleted_tag],
                publish_status=PublishStatusEnum.PUBLISHED,
                published_at="2024-01-01T00:00:00",
                created_at="2024-01-01T00:00:00",
                updated_at="2024-01-01T00:00:00",
            ),
        )

        public_result = await self.storage.get_note_by_slug(
            slug="test-note",
            include_deleted_tags=False,
        )
        admin_result = await self.storage.get_note_by_slug(
            slug="test-note",
            include_deleted_tags=True,
        )

        assert public_result.localized_title(language=LanguageEnum.RU) == "Test Note"
        assert [tag.slug for tag in public_result.tags] == ["python"]
        assert [tag.slug for tag in admin_result.tags] == ["python", "deleted"]

    async def test_get_note_by_slug_returns_canonical_translations(self) -> None:
        await self.storage_helper.create_note(
            note=self.factory.core.note(
                title_ru="Русская заметка",
                title_en="English note",
                content_ru="Русское содержимое",
                content_en="English content",
                folder_ru="Русская папка",
                folder_en="English folder",
                slug="localized-note",
            ),
        )

        result = await self.storage.get_note_by_slug(
            slug="localized-note",
            include_deleted_tags=False,
        )

        assert not hasattr(result, "title")
        assert not hasattr(result, "content")
        assert not hasattr(result, "folder")
        assert result.localized_title(language=LanguageEnum.RU) == "Русская заметка"
        assert result.localized_content(language=LanguageEnum.RU) == "Русское содержимое"
        assert result.localized_folder(language=LanguageEnum.RU) == "Русская папка"
        assert result.localized_title(language=LanguageEnum.EN) == "English note"
        assert result.localized_content(language=LanguageEnum.EN) == "English content"
        assert result.localized_folder(language=LanguageEnum.EN) == "English folder"

    async def test_get_note_by_slug_not_found(self) -> None:
        with pytest.raises(NoteNotFoundError):
            await self.storage.get_note_by_slug(
                slug="non-existent",
                include_deleted_tags=False,
            )

    async def test_list_notes_filters_by_active_tag_and_published_status(self) -> None:
        python = self.factory.core.tag(tag_id=IntId(1), slug="python")
        draft_tag = self.factory.core.tag(tag_id=IntId(2), slug="draft")
        await self.storage_helper.create_tags(tags=[python, draft_tag])
        await self.storage_helper.create_notes(
            notes=[
                self.factory.core.note(
                    title="Published Python",
                    slug="published-python",
                    tags=[python],
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-01T00:00:00",
                    created_at="2024-02-01T00:00:00",
                    updated_at="2024-02-01T00:00:00",
                ),
                self.factory.core.note(
                    title="Draft Python",
                    slug="draft-python",
                    tags=[python],
                    publish_status=PublishStatusEnum.DRAFT,
                    created_at="2024-03-01T00:00:00",
                    updated_at="2024-03-01T00:00:00",
                ),
                self.factory.core.note(
                    title="Other",
                    slug="other",
                    tags=[draft_tag],
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-04-01T00:00:00",
                    created_at="2024-04-01T00:00:00",
                    updated_at="2024-04-01T00:00:00",
                ),
            ],
        )

        result = await self.storage.list_notes(
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

        assert [note.slug for note in result.values] == ["published-python"]
        assert result.total_count == 1
        assert result.total_pages == 1

    async def test_list_notes_sorts_published_before_drafts_for_admin(self) -> None:
        await self.storage_helper.create_notes(
            notes=[
                self.factory.core.note(
                    title="Draft",
                    slug="draft",
                    publish_status=PublishStatusEnum.DRAFT,
                    created_at="2024-05-01T00:00:00",
                    updated_at="2024-05-01T00:00:00",
                ),
                self.factory.core.note(
                    title="Older Published",
                    slug="older-published",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-01-01T00:00:00",
                    created_at="2024-01-01T00:00:00",
                    updated_at="2024-01-01T00:00:00",
                ),
                self.factory.core.note(
                    title="Newer Published",
                    slug="newer-published",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-04-01T00:00:00",
                    created_at="2024-04-01T00:00:00",
                    updated_at="2024-04-01T00:00:00",
                ),
            ],
        )

        result = await self.storage.list_notes(
            filters=NoteFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=False,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query=None,
            ),
        )

        assert [note.slug for note in result.values] == [
            "newer-published",
            "older-published",
            "draft",
        ]

    async def test_list_notes_filters_by_inclusive_publish_date_range(self) -> None:
        await self.storage_helper.create_notes(
            notes=[
                self.factory.core.note(
                    title="Before",
                    slug="before",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-01-31T23:59:59",
                    created_at="2024-01-31T23:59:59",
                    updated_at="2024-01-31T23:59:59",
                ),
                self.factory.core.note(
                    title="Range Start",
                    slug="range-start",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-01T00:00:00",
                    created_at="2024-02-01T00:00:00",
                    updated_at="2024-02-01T00:00:00",
                ),
                self.factory.core.note(
                    title="Range End",
                    slug="range-end",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-29T23:59:59",
                    created_at="2024-02-29T23:59:59",
                    updated_at="2024-02-29T23:59:59",
                ),
                self.factory.core.note(
                    title="After",
                    slug="after",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-03-01T00:00:00",
                    created_at="2024-03-01T00:00:00",
                    updated_at="2024-03-01T00:00:00",
                ),
                self.factory.core.note(
                    title="Draft",
                    slug="draft",
                    publish_status=PublishStatusEnum.DRAFT,
                    created_at="2024-02-15T00:00:00",
                    updated_at="2024-02-15T00:00:00",
                ),
            ],
        )

        result = await self.storage.list_notes(
            filters=NoteFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=False,
                tag_slug=None,
                published_from=date(2024, 2, 1),
                published_to=date(2024, 2, 29),
                search_query=None,
            ),
        )

        assert [note.slug for note in result.values] == ["range-end", "range-start"]
        assert result.total_count == 2
        assert result.total_pages == 1

    async def test_list_notes_searches_by_title_and_content(self) -> None:
        await self.storage_helper.create_notes(
            notes=[
                self.factory.core.note(
                    title="PostgreSQL full text search",
                    content="Indexing notes without a table scan.",
                    slug="title-match",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-05-01T00:00:00",
                ),
                self.factory.core.note(
                    title="Dependency injection",
                    content="Dishka providers wire use cases to storage adapters.",
                    slug="content-match",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-04-01T00:00:00",
                ),
                self.factory.core.note(
                    title="Unrelated",
                    content="No matching terms here.",
                    slug="unrelated",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-06-01T00:00:00",
                ),
            ],
        )

        title_result = await self.storage.list_notes(
            filters=NoteFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query="full text",
            ),
        )
        content_result = await self.storage.list_notes(
            filters=NoteFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query="dishka providers",
            ),
        )

        assert [note.slug for note in title_result.values] == ["title-match"]
        assert [note.slug for note in content_result.values] == ["content-match"]

    async def test_list_notes_searches_only_requested_language_vector(self) -> None:
        await self.storage_helper.create_notes(
            notes=[
                self.factory.core.note(
                    title_ru="Очереди задач",
                    title_en="Task queues",
                    content_ru="Фоновая обработка заданий.",
                    content_en="Background job processing.",
                    slug="task-queues",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-05-01T00:00:00",
                ),
                self.factory.core.note(
                    title_ru="Индексы PostgreSQL",
                    title_en="Database indexes",
                    content_ru="Поиск по документам.",
                    content_en="Query planning details.",
                    slug="database-indexes",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-04-01T00:00:00",
                ),
            ],
        )

        ru_result = await self.storage.list_notes(
            filters=NoteFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query="документам",
            ),
        )
        en_result = await self.storage.list_notes(
            filters=NoteFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.EN,
                only_published=True,
                tag_slug=None,
                published_from=None,
                published_to=None,
                search_query="background",
            ),
        )

        assert [note.slug for note in ru_result.values] == ["database-indexes"]
        assert [note.slug for note in en_result.values] == ["task-queues"]

    async def test_list_notes_composes_tag_date_and_search_filters(self) -> None:
        python = self.factory.core.tag(tag_id=IntId(1), slug="python")
        database = self.factory.core.tag(tag_id=IntId(2), slug="database")
        await self.storage_helper.create_tags(tags=[python, database])
        await self.storage_helper.create_notes(
            notes=[
                self.factory.core.note(
                    title="Python database indexing",
                    content="PostgreSQL search vectors for notes.",
                    slug="match",
                    tags=[python],
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-10T00:00:00",
                ),
                self.factory.core.note(
                    title="Python old indexing",
                    content="PostgreSQL search vectors for notes.",
                    slug="old",
                    tags=[python],
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-01-10T00:00:00",
                ),
                self.factory.core.note(
                    title="Database indexing",
                    content="PostgreSQL search vectors for notes.",
                    slug="wrong-tag",
                    tags=[database],
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-10T00:00:00",
                ),
            ],
        )

        result = await self.storage.list_notes(
            filters=NoteFilters(
                page=1,
                page_size=10,
                language=LanguageEnum.RU,
                only_published=True,
                tag_slug="python",
                published_from=date(2024, 2, 1),
                published_to=date(2024, 2, 29),
                search_query="search vectors",
            ),
        )

        assert [note.slug for note in result.values] == ["match"]

    async def test_list_tree_groups_folders_and_hides_drafts_for_public(self) -> None:
        await self.storage_helper.create_notes(
            notes=[
                self.factory.core.note(
                    title="B Note",
                    slug="b-note",
                    folder="Backend",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-01-01T00:00:00",
                ),
                self.factory.core.note(
                    title="A Note",
                    slug="a-note",
                    folder="Architecture",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at="2024-02-01T00:00:00",
                ),
                self.factory.core.note(
                    title="Draft",
                    slug="draft",
                    folder="Architecture",
                    publish_status=PublishStatusEnum.DRAFT,
                ),
            ],
        )

        public_tree = await self.storage.list_tree(
            only_published=True,
            language=LanguageEnum.RU,
        )
        admin_tree = await self.storage.list_tree(
            only_published=False,
            language=LanguageEnum.RU,
        )

        assert [folder.folder for folder in public_tree.folders] == ["Architecture", "Backend"]
        assert [item.slug for item in public_tree.folders[0].notes] == ["a-note"]
        assert [item.slug for item in admin_tree.folders[0].notes] == ["a-note", "draft"]

    async def test_update_note_publish_status_sets_first_published_at_only_once(self) -> None:
        await self.storage_helper.create_note(
            note=self.factory.core.note(slug="draft", publish_status=PublishStatusEnum.DRAFT),
        )

        await self.storage.update_note_publish_status(
            slug="draft",
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        first = await self.storage.get_note_by_slug(
            slug="draft",
            include_deleted_tags=False,
        )
        await self.storage.update_note_publish_status(
            slug="draft",
            publish_status=PublishStatusEnum.DRAFT,
        )
        await self.storage.update_note_publish_status(
            slug="draft",
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        second = await self.storage.get_note_by_slug(
            slug="draft",
            include_deleted_tags=False,
        )

        assert first.published_at is not None
        assert second.published_at == first.published_at

    async def test_tag_soft_delete_and_restore(self) -> None:
        tag = self.factory.core.tag(tag_id=IntId(1), slug="python")
        await self.storage.create_tag(tag=tag)

        await self.storage.soft_delete_tag(tag_id=IntId(1))
        active_tags = await self.storage.list_tags(
            include_deleted=False,
            language=LanguageEnum.RU,
        )
        deleted_tags = await self.storage.list_tags(
            include_deleted=True,
            language=LanguageEnum.RU,
        )
        await self.storage.restore_tag(tag_id=IntId(1))
        restored_tags = await self.storage.list_tags(
            include_deleted=False,
            language=LanguageEnum.RU,
        )

        assert active_tags.values == []
        assert deleted_tags.values[0].deleted_at is not None
        assert [tag.slug for tag in restored_tags] == ["python"]

    async def test_update_unknown_tag_raises_not_found(self) -> None:
        with pytest.raises(TagNotFoundError):
            await self.storage.update_tag(
                tag=self.factory.core.tag(tag_id=IntId(999), name="Missing", slug="missing"),
            )
