import hashlib
from dataclasses import dataclass
from datetime import datetime

from core.files.exceptions import FileSizeTooLargeError
from core.files.file_name_generators import FileNameGenerator
from core.knowledge.files.clients import (
    KnowledgeFileClient,
    KnowledgeFileRollbackRegistrar,
    KnowledgePhotoProcessor,
)
from core.knowledge.files.enums import KnowledgeFileKind
from core.knowledge.files.schemas import (
    KnowledgeFile,
    KnowledgeFileContent,
    KnowledgeFileRules,
    KnowledgeFileUpdateParams,
    KnowledgeFileUploadParams,
)
from core.knowledge.files.storages import KnowledgeFilesStorage


@dataclass(kw_only=True, slots=True, frozen=True)
class KnowledgeFileCrudService:
    storage: KnowledgeFilesStorage
    client: KnowledgeFileClient
    photo_processor: KnowledgePhotoProcessor
    file_name_generator: FileNameGenerator
    rules: KnowledgeFileRules

    async def create_file(
        self,
        *,
        params: KnowledgeFileUploadParams,
        now: datetime,
        rollback_registrar: KnowledgeFileRollbackRegistrar,
    ) -> KnowledgeFile:
        rule = self.rules.require(kind=params.kind)
        params.validate(rule=rule)
        content = params.content
        mime_type = params.mime_type
        if params.kind == KnowledgeFileKind.PERSON_PHOTO:
            processed = self.photo_processor.process(params=params)
            content = processed.content
            mime_type = processed.mime_type
            if len(content) > rule.max_size_bytes:
                raise FileSizeTooLargeError(
                    size_bytes=len(content),
                    max_size_bytes=rule.max_size_bytes,
                )
        relative_path = self.file_name_generator(
            folder=rule.folder,
            file_extension=(
                ".webp" if params.kind == KnowledgeFileKind.PERSON_PHOTO else params.file_extension
            ),
        )
        file = KnowledgeFile(
            id=params.id,
            item_id=params.item_id,
            author_username=params.author_username,
            kind=params.kind,
            relative_path=relative_path,
            mime_type=mime_type,
            size_bytes=len(content),
            name=params.name.strip(),
            original_name=params.original_name,
            original_sha256=hashlib.sha256(params.content).hexdigest(),
            created_at=now,
            updated_at=now,
        )
        file = await self.storage.create_file(file=file)
        await self.client.upload_file(
            content=content,
            object_name=file.relative_path,
            content_type=file.mime_type,
        )
        rollback_registrar.register_new_object(object_name=file.relative_path)
        return file

    async def read_file(self, *, file_id: str, author_username: str) -> KnowledgeFileContent:
        file = await self.storage.get_file(
            file_id=file_id,
            author_username=author_username,
        )
        return KnowledgeFileContent(
            file=file,
            content=self.client.stream_file(object_name=file.relative_path),
        )

    async def rename_file(
        self,
        *,
        file: KnowledgeFile,
        params: KnowledgeFileUpdateParams,
        updated_at: datetime,
    ) -> KnowledgeFile:
        params.validate()
        return await self.storage.update_file_name(
            file=file,
            name=params.name.strip(),
            updated_at=updated_at,
        )

    async def delete_file(self, *, file: KnowledgeFile) -> KnowledgeFile:
        await self.storage.delete_file(file=file)
        return file
