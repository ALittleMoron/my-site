from collections.abc import AsyncGenerator
from unittest.mock import Mock, patch

import pytest
import pytest_asyncio

from config.settings import Settings
from core.files.exceptions import ContentTypeNotAllowedError
from core.files.file_storages import FileStorage
from core.files.use_cases import PresignPutObjectUseCase
from tests.fixtures import FactoryFixture, ContainerFixture


class TestPresignPutObjectUseCase(FactoryFixture, ContainerFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self, test_settings: Settings) -> AsyncGenerator[None, None]:
        self.mock_get_minio_object_url = Mock()
        self.file_name_generator = await self.container.get_file_name_generator()
        self.file_storage = Mock(spec=FileStorage)
        self.use_case = PresignPutObjectUseCase(
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
            await self.use_case.execute(params=params)

    async def test(self) -> None:
        self.file_storage.presign_put_object.return_value = "upload_url"
        self.mock_get_minio_object_url.return_value = "access_url"
        params = self.factory.core.presign_put_object_params(
            folder="my_folder",
            namespace="media",
            content_type="image/png",
        )
        urls = await self.use_case.execute(params=params)
        assert urls == self.factory.core.presign_put_object(
            upload_url="upload_url",
            access_url="access_url",
        )
