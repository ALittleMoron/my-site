from datetime import UTC, datetime
from io import BytesIO
from unittest.mock import Mock

import pytest
import pytest_asyncio

from core.files.clients import FileClient
from core.files.enums import FilePurpose
from core.files.exceptions import (
    ContentTypeNotAllowedError,
    FileInUseError,
    FileNameInvalidError,
    FilePurposeNotAllowedError,
    FileSizeTooLargeError,
)
from core.files.file_name_generators import FileNameGenerator
from core.files.schemas import (
    FileRead,
    FileRule,
    FileRules,
    FileUpdateParams,
    FileUploadParams,
    FileUploadResult,
    StoredFile,
)
from core.files.services import FileService
from core.files.storages import FileStorage
from tests.test_cases import TestCase


class TestFileService(TestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.now = datetime(2026, 7, 3, 10, 0, tzinfo=UTC)
        self.file_client = Mock(spec=FileClient)
        self.file_storage = Mock(spec=FileStorage)
        self.file_name_generator = Mock(spec=FileNameGenerator)
        self.file_name_generator.return_value = "article-content-images/file-id.png"
        self.service = FileService(
            file_client=self.file_client,
            file_storage=self.file_storage,
            file_name_generator=self.file_name_generator,
            namespace="media",
            rules=FileRules(
                values={
                    FilePurpose.ARTICLE_CONTENT_IMAGE: FileRule(
                        folder="article-content-images",
                        allowed_mime_types=frozenset({"image/png"}),
                        max_size_bytes=4,
                    ),
                    FilePurpose.ARTICLE_COVER_IMAGE: FileRule(
                        folder="article-cover-images",
                        allowed_mime_types=frozenset({"image/png"}),
                        max_size_bytes=8,
                    ),
                    FilePurpose.ATTACHMENT: FileRule(
                        folder="attachments",
                        allowed_mime_types=frozenset({"application/pdf"}),
                        max_size_bytes=16,
                    ),
                },
            ),
            now_factory=lambda: self.now,
        )

    async def test_upload_file_validates_uploads_and_persists_metadata(self) -> None:
        stored_file = StoredFile(
            id="file-id",
            purpose=FilePurpose.ARTICLE_CONTENT_IMAGE,
            namespace="media",
            relative_path="article-content-images/file-id.png",
            mime_type="image/png",
            size_bytes=4,
            name="Inline image",
            original_name="original.png",
            created_at=self.now,
            updated_at=self.now,
        )
        self.file_client.upload_file.return_value = FileUploadResult(
            url="https://s3.example.test/media/article-content-images/file-id.png",
            bucket="media",
            object_name="article-content-images/file-id.png",
            size=4,
        )
        self.file_client.get_access_url.return_value = (
            "https://s3.example.test/media/article-content-images/file-id.png"
        )
        self.file_storage.create_file.return_value = stored_file

        result = await self.service.upload_file(
            params=FileUploadParams(
                id="file-id",
                purpose=FilePurpose.ARTICLE_CONTENT_IMAGE,
                name="Inline image",
                original_name="original.png",
                mime_type="image/png",
                content=b"data",
            ),
        )

        assert result == FileRead(
            file=stored_file,
            access_url="https://s3.example.test/media/article-content-images/file-id.png",
            markdown_url="https://s3.example.test/media/article-content-images/file-id.png#fileId=file-id",
        )
        self.file_name_generator.assert_called_once_with(
            folder="article-content-images",
            file_extension=".png",
        )
        self.file_client.upload_file.assert_awaited_once()
        upload_call = self.file_client.upload_file.await_args.kwargs
        assert isinstance(upload_call["file_data"], BytesIO)
        assert upload_call["file_data"].getvalue() == b"data"
        assert upload_call["object_name"] == "article-content-images/file-id.png"
        assert upload_call["namespace"] == "media"
        assert upload_call["content_type"] == "image/png"
        self.file_storage.create_file.assert_awaited_once_with(file=stored_file)

    async def test_upload_file_does_not_write_object_when_metadata_write_fails(self) -> None:
        self.file_storage.create_file.side_effect = RuntimeError("db write failed")

        with pytest.raises(RuntimeError, match="db write failed"):
            await self.service.upload_file(
                params=FileUploadParams(
                    id="file-id",
                    purpose=FilePurpose.ARTICLE_CONTENT_IMAGE,
                    name="Inline image",
                    original_name="original.png",
                    mime_type="image/png",
                    content=b"data",
                ),
            )

        self.file_client.upload_file.assert_not_called()

    async def test_upload_file_rejects_disallowed_mime_type_before_external_io(self) -> None:
        with pytest.raises(ContentTypeNotAllowedError):
            await self.service.upload_file(
                params=FileUploadParams(
                    id="file-id",
                    purpose=FilePurpose.ARTICLE_CONTENT_IMAGE,
                    name="Inline image",
                    original_name="original.txt",
                    mime_type="text/plain",
                    content=b"data",
                ),
            )

        self.file_client.upload_file.assert_not_called()
        self.file_storage.create_file.assert_not_called()

    async def test_upload_file_rejects_too_large_content_before_external_io(self) -> None:
        with pytest.raises(FileSizeTooLargeError):
            await self.service.upload_file(
                params=FileUploadParams(
                    id="file-id",
                    purpose=FilePurpose.ARTICLE_CONTENT_IMAGE,
                    name="Inline image",
                    original_name="original.png",
                    mime_type="image/png",
                    content=b"large",
                ),
            )

        self.file_client.upload_file.assert_not_called()
        self.file_storage.create_file.assert_not_called()

    async def test_upload_file_rejects_blank_display_name_before_external_io(self) -> None:
        with pytest.raises(FileNameInvalidError):
            await self.service.upload_file(
                params=FileUploadParams(
                    id="file-id",
                    purpose=FilePurpose.ARTICLE_CONTENT_IMAGE,
                    name="   ",
                    original_name="original.png",
                    mime_type="image/png",
                    content=b"data",
                ),
            )

        self.file_client.upload_file.assert_not_called()
        self.file_storage.create_file.assert_not_called()

    async def test_update_file_name_returns_updated_file_with_access_url(self) -> None:
        stored_file = StoredFile(
            id="file-id",
            purpose=FilePurpose.ARTICLE_COVER_IMAGE,
            namespace="media",
            relative_path="article-cover-images/file-id.png",
            mime_type="image/png",
            size_bytes=4,
            name="Updated cover",
            original_name="cover.png",
            created_at=self.now,
            updated_at=self.now,
        )
        self.file_storage.update_file_name.return_value = stored_file
        self.file_client.get_access_url.return_value = (
            "https://s3.example.test/media/article-cover-images/file-id.png"
        )

        result = await self.service.update_file(
            file_id="file-id",
            params=FileUpdateParams(name="Updated cover"),
        )

        assert result == FileRead(
            file=stored_file,
            access_url="https://s3.example.test/media/article-cover-images/file-id.png",
            markdown_url="https://s3.example.test/media/article-cover-images/file-id.png#fileId=file-id",
        )
        self.file_storage.update_file_name.assert_awaited_once_with(
            file_id="file-id",
            name="Updated cover",
            updated_at=self.now,
        )
        self.file_client.upload_file.assert_not_called()

    async def test_update_file_name_rejects_blank_display_name_before_storage_call(self) -> None:
        with pytest.raises(FileNameInvalidError):
            await self.service.update_file(
                file_id="file-id",
                params=FileUpdateParams(name=" "),
            )

        self.file_storage.update_file_name.assert_not_called()

    async def test_ensure_files_allowed_accepts_files_with_expected_purpose(self) -> None:
        stored_file = StoredFile(
            id="cover-id",
            purpose=FilePurpose.ARTICLE_COVER_IMAGE,
            namespace="media",
            relative_path="article-cover-images/cover.png",
            mime_type="image/png",
            size_bytes=4,
            name="Cover",
            original_name="cover.png",
            created_at=self.now,
            updated_at=self.now,
        )
        self.file_storage.get_file.return_value = stored_file

        await self.service.ensure_files_allowed(
            file_ids=frozenset({"cover-id"}),
            purpose=FilePurpose.ARTICLE_COVER_IMAGE,
        )

        self.file_storage.get_file.assert_awaited_once_with(file_id="cover-id")

    async def test_ensure_files_allowed_rejects_files_with_different_purpose(self) -> None:
        stored_file = StoredFile(
            id="inline-id",
            purpose=FilePurpose.ARTICLE_CONTENT_IMAGE,
            namespace="media",
            relative_path="article-content-images/image.png",
            mime_type="image/png",
            size_bytes=4,
            name="Inline image",
            original_name="image.png",
            created_at=self.now,
            updated_at=self.now,
        )
        self.file_storage.get_file.return_value = stored_file

        with pytest.raises(FilePurposeNotAllowedError):
            await self.service.ensure_files_allowed(
                file_ids=frozenset({"inline-id"}),
                purpose=FilePurpose.ARTICLE_COVER_IMAGE,
            )

    async def test_delete_file_rejects_file_with_usages_before_external_io(self) -> None:
        self.file_storage.file_has_usages.return_value = True

        with pytest.raises(FileInUseError):
            await self.service.delete_file(file_id="file-id")

        self.file_client.delete_file.assert_not_called()
        self.file_storage.delete_file.assert_not_called()

    async def test_delete_file_deletes_object_before_metadata(self) -> None:
        stored_file = StoredFile(
            id="file-id",
            purpose=FilePurpose.ATTACHMENT,
            namespace="media",
            relative_path="attachments/file-id.pdf",
            mime_type="application/pdf",
            size_bytes=4,
            name="Attachment",
            original_name="attachment.pdf",
            created_at=self.now,
            updated_at=self.now,
        )
        self.file_storage.file_has_usages.return_value = False
        self.file_storage.get_file.return_value = stored_file

        await self.service.delete_file(file_id="file-id")

        self.file_client.delete_file.assert_awaited_once_with(
            object_name="attachments/file-id.pdf",
            namespace="media",
        )
        self.file_storage.delete_file.assert_awaited_once_with(file_id="file-id")
