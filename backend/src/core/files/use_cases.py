from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from core.files.file_name_generators import FileNameGenerator
from core.files.file_storages import FileStorage
from core.files.schemas import PresignPutObject, PresignPutObjectParams
from infra.config.constants import constants
from infra.config.settings import settings


class AbstractFilesUseCase(metaclass=ABCMeta):
    @abstractmethod
    async def presign_put_object(self, params: PresignPutObjectParams) -> PresignPutObject:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class FilesUseCase(AbstractFilesUseCase):
    file_storage: FileStorage
    file_name_generator: FileNameGenerator

    async def presign_put_object(self, params: PresignPutObjectParams) -> PresignPutObject:
        params.validate_content_type(allowed_types=constants.files.allowed_to_upload_media_types)
        file_name = self.file_name_generator(
            folder=params.folder,
            file_extension=params.file_extension,
        )
        upload_url = await self.file_storage.presign_put_object(
            object_name=file_name,
            namespace=params.namespace,
        )
        return PresignPutObject(
            upload_url=upload_url,
            access_url=settings.get_minio_object_url(
                bucket=params.namespace,
                object_path=file_name,
            ),
        )
