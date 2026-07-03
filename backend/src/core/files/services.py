from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO

from core.files.clients import FileClient
from core.files.enums import FilePurpose
from core.files.exceptions import FileInUseError, FilePurposeNotAllowedError
from core.files.file_name_generators import FileNameGenerator
from core.files.schemas import (
    FileRead,
    FileRules,
    FileUpdateParams,
    FileUploadParams,
    StoredFile,
)
from core.files.storages import FileStorage
from core.files.types import Namespace


@dataclass(kw_only=True, slots=True, frozen=True)
class FileService:
    file_client: FileClient
    file_storage: FileStorage
    file_name_generator: FileNameGenerator
    namespace: Namespace
    rules: FileRules
    now_factory: Callable[[], datetime]

    async def upload_file(self, *, params: FileUploadParams) -> FileRead:
        rule = self.rules.require(params.purpose)
        params.validate_name()
        params.validate_mime_type(allowed_mime_types=rule.allowed_mime_types)
        params.validate_size(max_size_bytes=rule.max_size_bytes)
        relative_path = self.file_name_generator(
            folder=rule.folder,
            file_extension=params.file_extension,
        )
        now = self.now_factory()
        file = StoredFile(
            id=params.id,
            purpose=params.purpose,
            namespace=self.namespace,
            relative_path=relative_path,
            mime_type=params.mime_type,
            size_bytes=params.size_bytes,
            name=params.name,
            original_name=params.original_name,
            created_at=now,
            updated_at=now,
        )
        file = await self.file_storage.create_file(file=file)
        await self.file_client.upload_file(
            file_data=BytesIO(params.content),
            object_name=relative_path,
            namespace=self.namespace,
            content_type=params.mime_type,
        )
        return self._to_read(file=file)

    async def get_file(self, *, file_id: str) -> FileRead:
        return self._to_read(file=await self.file_storage.get_file(file_id=file_id))

    async def list_files(self, *, purpose: FilePurpose) -> list[FileRead]:
        files = await self.file_storage.list_files(purpose=purpose)
        return [self._to_read(file=file) for file in files]

    async def update_file(self, *, file_id: str, params: FileUpdateParams) -> FileRead:
        params.validate_name()
        return self._to_read(
            file=await self.file_storage.update_file_name(
                file_id=file_id,
                name=params.name,
                updated_at=self.now_factory(),
            ),
        )

    async def ensure_files_allowed(
        self,
        *,
        file_ids: frozenset[str],
        purpose: FilePurpose,
    ) -> None:
        for file_id in sorted(file_ids):
            file = await self.file_storage.get_file(file_id=file_id)
            if file.purpose != purpose:
                raise FilePurposeNotAllowedError

    async def delete_file(self, *, file_id: str) -> None:
        if await self.file_storage.file_has_usages(file_id=file_id):
            raise FileInUseError
        file = await self.file_storage.get_file(file_id=file_id)
        await self.file_client.delete_file(
            object_name=file.relative_path,
            namespace=file.namespace,
        )
        await self.file_storage.delete_file(file_id=file_id)

    def _to_read(self, *, file: StoredFile) -> FileRead:
        access_url = self.file_client.get_access_url(
            object_name=file.relative_path,
            namespace=file.namespace,
        )
        return FileRead(
            file=file,
            access_url=access_url,
            markdown_url=f"{access_url}#fileId={file.id}",
        )
