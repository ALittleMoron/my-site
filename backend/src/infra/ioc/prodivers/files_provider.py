import secrets

from dishka import Provider, Scope, provide
from miniopy_async.api import Minio

from core.files.file_name_generators import FileNameGenerator, TimestampFileNameGenerator
from core.files.file_storages import FileStorage
from core.files.use_cases import AbstractFilesUseCase, FilesUseCase
from infra.config.settings import settings
from infra.minio.file_storages import MinioFileStorage


class FilesProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_file_name_generator(self) -> FileNameGenerator:
        return TimestampFileNameGenerator(
            random_suffix_length=4,
            random_generator=secrets.token_hex,
        )

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
    async def provide_files_use_case(
        self,
        file_storage: FileStorage,
        file_name_generator: FileNameGenerator,
    ) -> AbstractFilesUseCase:
        return FilesUseCase(
            file_storage=file_storage,
            file_name_generator=file_name_generator,
        )
