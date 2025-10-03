import uuid
from unittest.mock import Mock

from dishka import Provider, Scope, provide
from miniopy_async.api import Minio

from core.files.file_name_generators import FileNameGenerator, UUIDFileNameGenerator
from core.files.file_storages import FileStorage
from core.files.use_cases import AbstractPresignPutObjectUseCase


class MockFilesProvider(Provider):
    def __init__(self, uuid_: uuid.UUID | None = None):
        super().__init__()
        self.uuid_ = uuid_ or uuid.uuid4()

    @provide(scope=Scope.APP)
    async def provide_file_name_generator(self) -> FileNameGenerator:
        return UUIDFileNameGenerator(generator=lambda: self.uuid_)

    @provide(scope=Scope.APP)
    async def provide_minio_client(self) -> Minio:
        mock = Mock(spec=Minio)
        return mock

    @provide(scope=Scope.APP)
    async def provide_file_storage(self) -> FileStorage:
        mock = Mock(spec=FileStorage)
        return mock

    @provide(scope=Scope.APP)
    async def provide_presign_put_object_use_case(self) -> AbstractPresignPutObjectUseCase:
        mock = Mock(spec=AbstractPresignPutObjectUseCase)
        return mock
