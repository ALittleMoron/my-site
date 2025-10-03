from dishka import Provider, Scope, provide
from miniopy_async.api import Minio

from config.settings import settings
from core.files.file_name_generators import FileNameGenerator, UUIDFileNameGenerator
from core.files.file_storages import FileStorage
from core.files.use_cases import AbstractPresignPutObjectUseCase, PresignPutObjectUseCase
from file_storages.minio import MinioFileStorage


class FilesProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_file_name_generator(self) -> FileNameGenerator:
        return UUIDFileNameGenerator()

    @provide(scope=Scope.APP)
    async def provide_minio_client(self) -> Minio:
        return Minio(
            endpoint=settings.minio.endpoint,
            access_key=settings.minio.access_key,
            secret_key=settings.minio.secret_key.get_secret_value(),
            secure=settings.minio.secure,
        )

    @provide(scope=Scope.APP)
    async def provide_file_storage(self, minio_client: Minio) -> FileStorage:
        return MinioFileStorage(client=minio_client)

    @provide(scope=Scope.REQUEST)
    async def provide_presign_put_object_use_case(
        self,
        file_storage: FileStorage,
        file_name_generator: FileNameGenerator,
    ) -> AbstractPresignPutObjectUseCase:
        return PresignPutObjectUseCase(
            file_storage=file_storage,
            file_name_generator=file_name_generator,
        )
