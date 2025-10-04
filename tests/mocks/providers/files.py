import time
import uuid
from unittest.mock import Mock

from dishka import Provider, Scope, provide
from miniopy_async.api import Minio

from core.files.file_name_generators import FileNameGenerator, TimestampFileNameGenerator
from core.files.file_storages import FileStorage
from core.files.use_cases import AbstractPresignPutObjectUseCase


class MockFilesProvider(Provider):
    def __init__(self, timestamp: int | None = None, random_suffix: str | None = None):
        super().__init__()
        self.timestamp = timestamp or int(time.time() * 1_000_000)
        self.random_suffix = random_suffix or "abcd1234"

    @provide(scope=Scope.APP)
    async def provide_file_name_generator(self) -> FileNameGenerator:
        def mock_call(folder: str | None = None, file_extension: str = "") -> str:
            normalized_extension = FileNameGenerator.normalize_extension(file_extension)
            file_name = f"{self.timestamp}_{self.random_suffix}{normalized_extension}"
            path = "/".join([(folder or "").strip("/"), file_name])
            return path.removeprefix("/")

        mock_generator = Mock(spec=FileNameGenerator, side_effect=mock_call)

        return mock_generator

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
