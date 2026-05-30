import pytest
import pytest_asyncio

from core.enums import PublishStatusEnum
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

        assert public_result.title == "Test Note"
        assert [tag.slug for tag in public_result.tags] == ["python"]
        assert [tag.slug for tag in admin_result.tags] == ["python", "deleted"]

    async def test_get_note_by_slug_not_found(self) -> None:
        with pytest.raises(NoteNotFoundError):
            await self.storage.get_note_by_slug(slug="non-existent", include_deleted_tags=False)

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
                only_published=True,
                tag_slug="python",
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
            filters=NoteFilters(page=1, page_size=10, only_published=False, tag_slug=None),
        )

        assert [note.slug for note in result.values] == [
            "newer-published",
            "older-published",
            "draft",
        ]

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

        public_tree = await self.storage.list_tree(only_published=True)
        admin_tree = await self.storage.list_tree(only_published=False)

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
        first = await self.storage.get_note_by_slug(slug="draft", include_deleted_tags=False)
        await self.storage.update_note_publish_status(
            slug="draft",
            publish_status=PublishStatusEnum.DRAFT,
        )
        await self.storage.update_note_publish_status(
            slug="draft",
            publish_status=PublishStatusEnum.PUBLISHED,
        )
        second = await self.storage.get_note_by_slug(slug="draft", include_deleted_tags=False)

        assert first.published_at is not None
        assert second.published_at == first.published_at

    async def test_tag_soft_delete_and_restore(self) -> None:
        tag = self.factory.core.tag(tag_id=IntId(1), slug="python")
        await self.storage.create_tag(tag=tag)

        await self.storage.soft_delete_tag(tag_id=IntId(1))
        active_tags = await self.storage.list_tags(include_deleted=False)
        deleted_tags = await self.storage.list_tags(include_deleted=True)
        await self.storage.restore_tag(tag_id=IntId(1))
        restored_tags = await self.storage.list_tags(include_deleted=False)

        assert active_tags.values == []
        assert deleted_tags.values[0].deleted_at is not None
        assert [tag.slug for tag in restored_tags] == ["python"]

    async def test_update_unknown_tag_raises_not_found(self) -> None:
        with pytest.raises(TagNotFoundError):
            await self.storage.update_tag(
                tag=self.factory.core.tag(tag_id=IntId(999), name="Missing", slug="missing"),
            )
