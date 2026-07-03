from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError

from core.exceptions import EntryNotFoundError
from core.files.enums import FilePurpose
from infra.postgresql.storages.files import FilesDatabaseStorage
from tests.test_cases import StorageTestCase


class TestFilesDatabaseStorage(StorageTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.storage = FilesDatabaseStorage(session=self.db_session)

    async def test_create_get_list_update_and_delete_file(self) -> None:
        older = self.factory.core.stored_file(
            file_id=1,
            purpose=FilePurpose.ARTICLE_CONTENT_IMAGE,
            relative_path="article-content-images/older.png",
            name="Older",
            original_name="older.png",
            created_at=datetime(2026, 7, 3, 10, 0, tzinfo=UTC),
            updated_at=datetime(2026, 7, 3, 10, 0, tzinfo=UTC),
        )
        newer = self.factory.core.stored_file(
            file_id=2,
            purpose=FilePurpose.ARTICLE_CONTENT_IMAGE,
            relative_path="article-content-images/newer.png",
            name="Newer",
            original_name="newer.png",
            created_at=datetime(2026, 7, 3, 11, 0, tzinfo=UTC),
            updated_at=datetime(2026, 7, 3, 11, 0, tzinfo=UTC),
        )
        attachment = self.factory.core.stored_file(
            file_id=3,
            purpose=FilePurpose.ATTACHMENT,
            relative_path="attachments/document.pdf",
            mime_type="application/pdf",
            name="Document",
            original_name="document.pdf",
        )

        created = await self.storage.create_file(file=older)
        await self.storage.create_file(file=newer)
        await self.storage.create_file(file=attachment)

        result = await self.storage.get_file(file_id=older.id)
        article_images = await self.storage.list_files(
            purpose=FilePurpose.ARTICLE_CONTENT_IMAGE,
        )
        renamed = await self.storage.update_file_name(
            file_id=older.id,
            name="Renamed older",
            updated_at=datetime(2026, 7, 3, 12, 0, tzinfo=UTC),
        )
        await self.storage.delete_file(file_id=older.id)

        assert created == older
        assert result == older
        assert [file.id for file in article_images] == [newer.id, older.id]
        assert renamed.name == "Renamed older"
        assert renamed.updated_at == datetime(2026, 7, 3, 12, 0, tzinfo=UTC)
        with pytest.raises(EntryNotFoundError):
            await self.storage.get_file(file_id=older.id)

    async def test_file_has_usages_checks_article_cover_and_content_links(self) -> None:
        cover = self.factory.core.stored_file(
            file_id=10,
            purpose=FilePurpose.ARTICLE_COVER_IMAGE,
            relative_path="article-cover-images/cover.png",
            name="Cover",
            original_name="cover.png",
        )
        content = self.factory.core.stored_file(
            file_id=11,
            purpose=FilePurpose.ARTICLE_CONTENT_IMAGE,
            relative_path="article-content-images/content.png",
            name="Content image",
            original_name="content.png",
        )
        unused = self.factory.core.stored_file(
            file_id=12,
            purpose=FilePurpose.ATTACHMENT,
            relative_path="attachments/unused.txt",
            mime_type="text/plain",
            name="Unused",
            original_name="unused.txt",
        )
        await self.storage.create_file(file=cover)
        await self.storage.create_file(file=content)
        await self.storage.create_file(file=unused)
        await self.storage_helper.create_article(
            article=self.factory.core.article(
                slug="managed-file-usages",
                cover_image_file_id=cover.id,
                content_file_ids=frozenset({content.id}),
            ),
        )

        assert await self.storage.file_has_usages(file_id=cover.id)
        assert await self.storage.file_has_usages(file_id=content.id)
        assert not await self.storage.file_has_usages(file_id=unused.id)

    async def test_delete_file_is_restricted_by_article_foreign_keys(self) -> None:
        cover = self.factory.core.stored_file(
            file_id=20,
            purpose=FilePurpose.ARTICLE_COVER_IMAGE,
            relative_path="article-cover-images/restricted-cover.png",
            name="Restricted cover",
            original_name="cover.png",
        )
        await self.storage.create_file(file=cover)
        await self.storage_helper.create_article(
            article=self.factory.core.article(
                slug="delete-restricted-by-cover",
                cover_image_file_id=cover.id,
            ),
        )

        with pytest.raises(IntegrityError):
            await self.storage.delete_file(file_id=cover.id)
        await self.db_session.rollback()
