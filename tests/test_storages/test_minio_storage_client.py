from io import BytesIO
from unittest.mock import Mock, patch

import pytest
from miniopy_async.api import Minio
from miniopy_async.error import MinioException

from core.file_storages.exceptions import FileStorageInternalError
from core.file_storages.schemas import FileUploadResult
from file_storages.minio import MinioFileStorage


class TestMinioFileStorage:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.mock_minio_client = Mock(spec=Minio)
        self.storage = MinioFileStorage(client=self.mock_minio_client)

    async def test_ensure_bucket_exists_bucket_exists(self) -> None:
        bucket_name = "static"
        self.mock_minio_client.bucket_exists.return_value = True

        await self.storage.ensure_namespace_exists(bucket_name)

        self.mock_minio_client.bucket_exists.assert_called_once_with(bucket_name)
        self.mock_minio_client.make_bucket.assert_not_called()
        self.mock_minio_client.set_bucket_policy.assert_called_once()

    async def test_ensure_bucket_exists_bucket_not_exists(self) -> None:
        bucket_name = "media"
        self.mock_minio_client.bucket_exists.return_value = False

        await self.storage.ensure_namespace_exists(bucket_name)

        self.mock_minio_client.bucket_exists.assert_called_once_with(bucket_name)
        self.mock_minio_client.make_bucket.assert_called_once_with(bucket_name=bucket_name)
        self.mock_minio_client.set_bucket_policy.assert_called_once()

    @patch("file_storages.minio.settings")
    async def test_upload_file_success(self, mock_settings) -> None:
        mock_settings.get_minio_object_url.return_value = "http://localhost/media/test.txt"

        file_data = BytesIO(b"test content")
        object_name = "test.txt"
        content_type = "text/plain"

        mock_result = Mock()
        mock_result.size = 12

        self.mock_minio_client.bucket_exists.return_value = True
        self.mock_minio_client.put_object.return_value = mock_result

        result = await self.storage.upload_static_file(
            file_data=file_data,
            object_name=object_name,
            content_type=content_type,
        )

        expected_result = FileUploadResult(
            url="http://localhost/media/test.txt",
            bucket="static",
            object_name=object_name,
            size=12,
        )

        assert result == expected_result
        self.mock_minio_client.put_object.assert_called_once_with(
            bucket_name="static",
            object_name=object_name,
            data=file_data,
            length=12,
            content_type=content_type,
        )
        mock_settings.get_minio_object_url.assert_called_once_with(
            bucket="static",
            object_path=object_name,
        )

    async def test_upload_file_minio_exception(self) -> None:
        file_data = BytesIO(b"test content")
        object_name = "test.txt"

        self.mock_minio_client.bucket_exists.return_value = True
        self.mock_minio_client.put_object.side_effect = MinioException("Upload failed")

        with pytest.raises(FileStorageInternalError, match="File upload failed"):
            await self.storage.upload_static_file(
                file_data=file_data,
                object_name=object_name,
            )

    async def test_init_storage(self) -> None:
        with patch.object(self.storage, "ensure_namespace_exists") as mock_ensure:
            mock_ensure.return_value = None

            await self.storage.init_storage()

            assert mock_ensure.call_count == 2
            mock_ensure.assert_any_call(namespace="static")
            mock_ensure.assert_any_call(namespace="media")
