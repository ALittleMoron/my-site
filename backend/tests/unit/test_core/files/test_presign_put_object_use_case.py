from unittest.mock import Mock

import pytest
import pytest_asyncio

from core.files.exceptions import ContentTypeNotAllowedError
from core.files.file_storages import FileStorage
from core.files.use_cases import FilesUseCase
from tests.test_cases import ContainerTestCase


class TestFilesUseCase(ContainerTestCase):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.file_name_generator = await self.container.get_file_name_generator()
        self.file_storage = Mock(spec=FileStorage)
        self.use_case = FilesUseCase(
            file_storage=self.file_storage,
            file_name_generator=self.file_name_generator,
            allowed_upload_media_types={"image/png", "image/jpeg", "image/webp", "image/gif"},
        )

    async def test_not_valid_content_type(self) -> None:
        params = self.factory.core.presign_put_object_params(content_type="NOT_VALID")
        with pytest.raises(ContentTypeNotAllowedError):
            await self.use_case.presign_put_object(params=params)
        self.file_storage.presign_put_object.assert_not_called()

    async def test(self) -> None:
        self.file_storage.presign_put_object.return_value = self.factory.core.presign_put_object(
            upload_url="upload_url",
            access_url="access_url",
        )
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
        self.file_storage.presign_put_object.assert_called_once()
        call_args = self.file_storage.presign_put_object.call_args
        assert call_args.kwargs["content_type"] == "image/png"

    async def test_file_extension_in_file_name(self) -> None:
        self.file_storage.presign_put_object.return_value = self.factory.core.presign_put_object(
            upload_url="upload_url",
            access_url="access_url",
        )

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
