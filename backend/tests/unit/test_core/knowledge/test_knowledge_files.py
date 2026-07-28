from dataclasses import replace
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from core.files.exceptions import (
    ContentTypeNotAllowedError,
    FileNameInvalidError,
    FileSizeTooLargeError,
    InvalidFileDataError,
)
from core.knowledge.exceptions import KnowledgeFileNotFoundError
from core.knowledge.files.clients import (
    KnowledgeFileClient,
    KnowledgeFileRollbackRegistrar,
    KnowledgePhotoProcessor,
)
from core.knowledge.files.enums import KnowledgeFileKind
from core.knowledge.files.schemas import (
    KnowledgeFile,
    KnowledgeFileMutationResult,
    KnowledgeFileRule,
    KnowledgeFileRules,
    KnowledgeFileUpdateParams,
    KnowledgeFileUploadParams,
    ProcessedKnowledgePhoto,
)
from core.knowledge.files.services import KnowledgeFileCrudService
from core.knowledge.files.storages import KnowledgeFilesStorage
from core.knowledge.files.use_cases import KnowledgeFilesUseCase
from core.knowledge.items.enums import KnowledgeItemKind
from core.knowledge.items.schemas import KnowledgeItem
from core.knowledge.items.storages import KnowledgeItemsStorage
from tests.test_cases import TestCase

NOW = datetime(2026, 7, 27, 12, 0, tzinfo=UTC)


class TestKnowledgeFileCrudService(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=KnowledgeFilesStorage)
        self.client = Mock(spec=KnowledgeFileClient)
        self.photo_processor = Mock(spec=KnowledgePhotoProcessor)
        self.rollback_registrar = Mock(spec=KnowledgeFileRollbackRegistrar)
        self.file_name_generator = Mock(return_value="attachments/object.bin")
        self.rules = KnowledgeFileRules(
            values={
                KnowledgeFileKind.ATTACHMENT: KnowledgeFileRule(
                    folder="attachments",
                    allowed_mime_types=frozenset({"*/*"}),
                    max_size_bytes=20,
                    original_name_max_length=255,
                    mime_type_max_length=255,
                ),
                KnowledgeFileKind.PERSON_PHOTO: KnowledgeFileRule(
                    folder="person-photos",
                    allowed_mime_types=frozenset(
                        {"image/jpeg", "image/png", "image/webp"},
                    ),
                    max_size_bytes=5,
                    original_name_max_length=255,
                    mime_type_max_length=255,
                ),
            },
        )
        self.service = KnowledgeFileCrudService(
            storage=self.storage,
            client=self.client,
            photo_processor=self.photo_processor,
            file_name_generator=self.file_name_generator,
            rules=self.rules,
        )

    async def test_attachment_upload_persists_private_metadata_and_object(self) -> None:
        params = KnowledgeFileUploadParams(
            id="1" * 32,
            item_id="2" * 32,
            author_username="owner",
            kind=KnowledgeFileKind.ATTACHMENT,
            name=" Notes ",
            original_name="notes.txt",
            mime_type="text/plain",
            content=b"private",
        )
        self.storage.create_file.side_effect = lambda *, file: file

        result = await self.service.create_file(
            params=params,
            now=NOW,
            rollback_registrar=self.rollback_registrar,
        )

        assert result.name == "Notes"
        assert result.original_sha256
        assert result.relative_path == "attachments/object.bin"
        self.photo_processor.process.assert_not_called()
        self.client.upload_file.assert_awaited_once()
        self.rollback_registrar.register_new_object.assert_called_once_with(
            object_name="attachments/object.bin",
        )

    async def test_photo_upload_always_uses_processed_webp(self) -> None:
        params = KnowledgeFileUploadParams(
            id="1" * 32,
            item_id="2" * 32,
            author_username="owner",
            kind=KnowledgeFileKind.PERSON_PHOTO,
            name="Photo",
            original_name="photo.png",
            mime_type="image/png",
            content=b"png",
        )
        self.photo_processor.process.return_value = ProcessedKnowledgePhoto(
            content=b"webp",
            mime_type="image/webp",
        )
        self.storage.create_file.side_effect = lambda *, file: file

        result = await self.service.create_file(
            params=params,
            now=NOW,
            rollback_registrar=self.rollback_registrar,
        )

        assert result.mime_type == "image/webp"
        self.client.upload_file.assert_awaited_once()
        self.rollback_registrar.register_new_object.assert_called_once_with(
            object_name="attachments/object.bin",
        )

    @pytest.mark.parametrize(
        ("params", "error"),
        [
            (
                KnowledgeFileUploadParams(
                    id="1" * 32,
                    item_id="2" * 32,
                    author_username="owner",
                    kind=KnowledgeFileKind.ATTACHMENT,
                    name=" ",
                    original_name="file.txt",
                    mime_type="text/plain",
                    content=b"x",
                ),
                FileNameInvalidError,
            ),
            (
                KnowledgeFileUploadParams(
                    id="1" * 32,
                    item_id="2" * 32,
                    author_username="owner",
                    kind=KnowledgeFileKind.PERSON_PHOTO,
                    name="Photo",
                    original_name="file.gif",
                    mime_type="image/gif",
                    content=b"x",
                ),
                ContentTypeNotAllowedError,
            ),
            (
                KnowledgeFileUploadParams(
                    id="1" * 32,
                    item_id="2" * 32,
                    author_username="owner",
                    kind=KnowledgeFileKind.PERSON_PHOTO,
                    name="Photo",
                    original_name="file.png",
                    mime_type="image/png",
                    content=b"123456",
                ),
                FileSizeTooLargeError,
            ),
            (
                KnowledgeFileUploadParams(
                    id="1" * 32,
                    item_id="2" * 32,
                    author_username="owner",
                    kind=KnowledgeFileKind.ATTACHMENT,
                    name="File",
                    original_name="x" * 256,
                    mime_type="text/plain",
                    content=b"x",
                ),
                FileNameInvalidError,
            ),
            (
                KnowledgeFileUploadParams(
                    id="1" * 32,
                    item_id="2" * 32,
                    author_username="owner",
                    kind=KnowledgeFileKind.ATTACHMENT,
                    name="File",
                    original_name="file.txt",
                    mime_type="x" * 256,
                    content=b"x",
                ),
                InvalidFileDataError,
            ),
        ],
    )
    async def test_upload_rejects_invalid_input(
        self,
        params: KnowledgeFileUploadParams,
        error: type[Exception],
    ) -> None:
        with pytest.raises(error):
            await self.service.create_file(
                params=params,
                now=NOW,
                rollback_registrar=self.rollback_registrar,
            )


class TestKnowledgeFilesUseCase(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.item_storage = Mock(spec=KnowledgeItemsStorage)
        self.file_storage = Mock(spec=KnowledgeFilesStorage)
        self.file_service = Mock(spec=KnowledgeFileCrudService)
        self.use_case = KnowledgeFilesUseCase(
            item_storage=self.item_storage,
            file_storage=self.file_storage,
            file_service=self.file_service,
        )
        self.item = KnowledgeItem(
            id="1" * 32,
            kind=KnowledgeItemKind.PERSON,
            author_username="owner",
            display_name="Person",
            description="",
            tags=[],
            created_at=NOW,
            updated_at=NOW,
        )
        self.file = KnowledgeFile(
            id="2" * 32,
            item_id=self.item.id,
            author_username="owner",
            kind=KnowledgeFileKind.ATTACHMENT,
            relative_path="attachments/private.bin",
            mime_type="application/octet-stream",
            size_bytes=7,
            name="Private",
            original_name="private.bin",
            original_sha256="a" * 64,
            created_at=NOW,
            updated_at=NOW,
        )

    async def test_rename_rejects_foreign_nested_file_as_not_found(self) -> None:
        self.item_storage.get_item_for_author.return_value = self.item
        self.file_storage.get_file.return_value = replace(self.file, item_id="3" * 32)

        with pytest.raises(KnowledgeFileNotFoundError):
            await self.use_case.rename_attachment(
                item_id=self.item.id,
                file_id=self.file.id,
                author_username="owner",
                params=KnowledgeFileUpdateParams(name="Renamed"),
            )

    async def test_delete_attachment_returns_post_commit_cleanup_path(self) -> None:
        self.item_storage.get_item_for_author.return_value = self.item
        self.file_storage.get_file.return_value = self.file
        self.file_service.delete_file.return_value = self.file

        result = await self.use_case.delete_attachment(
            item_id=self.item.id,
            file_id=self.file.id,
            author_username="owner",
        )

        assert result == KnowledgeFileMutationResult(
            file=None,
            object_names_to_delete=("attachments/private.bin",),
        )
        self.item_storage.touch_items.assert_awaited_once()
