from dataclasses import dataclass

from core.files.file_name_generators import FileNameGenerator
from core.files.file_storages import FileStorage
from core.files.schemas import PresignPutObject, PresignPutObjectParams


@dataclass(kw_only=True, slots=True, frozen=True)
class FilesUseCase:
    file_storage: FileStorage
    file_name_generator: FileNameGenerator
    allowed_upload_media_types: set[str] | list[str] | tuple[str, ...]

    async def presign_put_object(self, params: PresignPutObjectParams) -> PresignPutObject:
        params.validate_content_type(allowed_types=self.allowed_upload_media_types)
        file_name = self.file_name_generator(
            folder=params.folder,
            file_extension=params.file_extension,
        )
        return await self.file_storage.presign_put_object(
            object_name=file_name,
            namespace=params.namespace,
            content_type=params.content_type,
        )
