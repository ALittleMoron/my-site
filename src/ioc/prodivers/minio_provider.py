from dishka import Provider, Scope, provide
from miniopy_async.api import Minio

from config.settings import settings
from core.file_storages.storages import FileStorage
from file_storages.minio import MinioFileStorage


class MinioProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_minio_client(self) -> Minio:
        return Minio(
            endpoint=settings.minio.endpoint,
            access_key=settings.minio.access_key,
            secret_key=settings.minio.secret_key.get_secret_value(),
            secure=settings.minio.secure,
        )

    @provide(scope=Scope.APP)
    async def provide_file_storage(self) -> FileStorage:
        minio_client = await self.provide_minio_client()
        return MinioFileStorage(client=minio_client)
