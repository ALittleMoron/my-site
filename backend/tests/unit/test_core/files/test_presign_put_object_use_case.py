from collections.abc import AsyncGenerator
from unittest.mock import Mock, patch

import pytest
import pytest_asyncio

from core.files.exceptions import ContentTypeNotAllowedError
from core.files.file_storages import FileStorage
from core.files.use_cases import FilesUseCase
from infra.config.settings import Settings
from tests.unit.fixtures import ContainerFixture, FactoryFixture


class TestFilesUseCase(FactoryFixture, ContainerFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self, test_settings: Settings) -> AsyncGenerator[None]:
        self.mock_get_minio_object_url = Mock()
        self.file_name_generator = await self.container.get_file_name_generator()
        self.file_storage = Mock(spec=FileStorage)
        self.use_case = FilesUseCase(
            file_storage=self.file_storage,
            file_name_generator=self.file_name_generator,
        )
        with patch.object(
            test_settings,
            "get_minio_object_url",
            new=self.mock_get_minio_object_url,
        ):
            yield

    async def test_not_valid_content_type(self) -> None:
        self.file_storage.presign_put_object.return_value = "upload_url"
        self.mock_get_minio_object_url.return_value = "access_url"
        params = self.factory.core.presign_put_object_params(content_type="NOT_VALID")
        with pytest.raises(ContentTypeNotAllowedError):
            await self.use_case.presign_put_object(params=params)

    async def test(self) -> None:
        self.file_storage.presign_put_object.return_value = "upload_url"
        self.mock_get_minio_object_url.return_value = "access_url"
        params = self.factory.core.presign_put_object_params(
            folder="my_folder",
            namespace="media",
            content_type="image/png",
        )
        urls = await self.use_case.presign_put_object(params=params)
        assert urls == self.factory.core.presign_put_object(
            upload_url="upload_url",
            access_url="access_url",
        )

    async def test_file_extension_in_file_name(self) -> None:
        self.file_storage.presign_put_object.return_value = "upload_url"
        self.mock_get_minio_object_url.return_value = "access_url"

        params = self.factory.core.presign_put_object_params(
            folder="images",
            namespace="media",
            content_type="image/png",
        )
        await self.use_case.presign_put_object(params=params)

        # Проверяем, что имя файла содержит расширение.
        call_args = self.file_storage.presign_put_object.call_args
        object_name = call_args.kwargs["object_name"]
        assert object_name.endswith(".png")
