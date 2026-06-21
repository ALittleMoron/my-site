import json
from io import BytesIO
from unittest.mock import AsyncMock, Mock, patch

import pytest
from botocore.exceptions import ClientError

from core.files.exceptions import FileStorageInternalError, NamespaceNotAllowedError
from core.files.schemas import FileUploadResult, PresignPutObject
from infra.s3.file_storages import S3ClientBundle, S3FileStorage


def create_client_error(code: str, operation_name: str = "HeadBucket") -> ClientError:
    return ClientError(
        error_response={
            "Error": {
                "Code": code,
                "Message": "S3 operation failed",
            },
        },
        operation_name=operation_name,
    )


def create_s3_client_double() -> Mock:
    client = Mock()
    client.head_bucket = AsyncMock()
    client.create_bucket = AsyncMock()
    client.put_bucket_policy = AsyncMock()
    client.put_bucket_cors = AsyncMock()
    client.put_object = AsyncMock()
    client.generate_presigned_url = AsyncMock()
    return client


class TestS3FileStorage:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.internal_client = create_s3_client_double()
        self.public_client = create_s3_client_double()
        self.storage = S3FileStorage(
            clients=S3ClientBundle(
                internal=self.internal_client,
                public=self.public_client,
            ),
        )

    async def test_ensure_bucket_exists_bucket_exists(self) -> None:
        bucket_name = "media"
        self.internal_client.head_bucket.return_value = {}

        await self.storage.ensure_namespace_exists(bucket_name)

        self.internal_client.head_bucket.assert_awaited_once_with(Bucket=bucket_name)
        self.internal_client.create_bucket.assert_not_awaited()
        self.internal_client.put_bucket_policy.assert_awaited_once()
        self.internal_client.put_bucket_cors.assert_awaited_once()

    async def test_ensure_bucket_exists_bucket_not_exists(self) -> None:
        bucket_name = "media"
        self.internal_client.head_bucket.side_effect = create_client_error("404")

        await self.storage.ensure_namespace_exists(bucket_name)

        self.internal_client.head_bucket.assert_awaited_once_with(Bucket=bucket_name)
        self.internal_client.create_bucket.assert_awaited_once_with(Bucket=bucket_name)
        self.internal_client.put_bucket_policy.assert_awaited_once()
        self.internal_client.put_bucket_cors.assert_awaited_once()

    async def test_ensure_bucket_exists_sets_public_read_policy_and_upload_cors(self) -> None:
        bucket_name = "media"
        self.internal_client.head_bucket.return_value = {}

        with patch("infra.s3.file_storages.settings") as mock_settings:
            mock_settings.public_app_origin = "https://alittlemoron.ru"
            mock_settings.minio.presign_put_expires_seconds = 300
            await self.storage.ensure_namespace_exists(bucket_name)

        policy_call = self.internal_client.put_bucket_policy.await_args.kwargs
        assert policy_call["Bucket"] == bucket_name
        assert json.loads(policy_call["Policy"]) == self.storage.create_bucket_policy(
            bucket_name=bucket_name,
        )
        self.internal_client.put_bucket_cors.assert_awaited_once_with(
            Bucket=bucket_name,
            CORSConfiguration={
                "CORSRules": [
                    {
                        "AllowedHeaders": ["*"],
                        "AllowedMethods": ["GET", "PUT"],
                        "AllowedOrigins": ["https://alittlemoron.ru"],
                        "ExposeHeaders": ["ETag"],
                        "MaxAgeSeconds": 300,
                    },
                ],
            },
        )

    async def test_ensure_bucket_exists_tolerates_unsupported_bucket_cors(self) -> None:
        bucket_name = "media"
        self.internal_client.head_bucket.return_value = {}
        self.internal_client.put_bucket_cors.side_effect = create_client_error(
            code="NotImplemented",
            operation_name="PutBucketCors",
        )

        await self.storage.ensure_namespace_exists(bucket_name)

        self.internal_client.put_bucket_policy.assert_awaited_once()
        self.internal_client.put_bucket_cors.assert_awaited_once()

    @patch("infra.s3.file_storages.settings")
    async def test_upload_file_success(self, mock_settings: Mock) -> None:
        mock_settings.get_minio_object_url.return_value = "http://localhost/media/test.txt"
        file_data = BytesIO(b"test content")
        object_name = "test.txt"
        content_type = "text/plain"
        self.internal_client.head_bucket.return_value = {}
        self.internal_client.put_object.return_value = {}

        result = await self.storage.upload_file(
            file_data=file_data,
            object_name=object_name,
            namespace="media",
            content_type=content_type,
        )
        expected_result = FileUploadResult(
            url="http://localhost/media/test.txt",
            bucket="media",
            object_name=object_name,
            size=12,
        )
        assert result == expected_result
        self.internal_client.put_object.assert_awaited_once_with(
            Bucket="media",
            Key=object_name,
            Body=b"test content",
            ContentType=content_type,
        )
        mock_settings.get_minio_object_url.assert_called_once_with(
            bucket="media",
            object_path=object_name,
        )

    async def test_ensure_namespace_valid(self) -> None:
        file_data = BytesIO(b"test content")
        object_name = "test.txt"
        self.internal_client.head_bucket.return_value = {}
        with pytest.raises(NamespaceNotAllowedError):
            await self.storage.upload_file(
                file_data=file_data,
                object_name=object_name,
                namespace="NOT_VALID",
                content_type=None,
            )

    async def test_upload_file_minio_exception(self) -> None:
        file_data = BytesIO(b"test content")
        object_name = "test.txt"
        self.internal_client.head_bucket.return_value = {}
        self.internal_client.put_object.side_effect = create_client_error("500")
        with pytest.raises(FileStorageInternalError, match="File upload failed"):
            await self.storage.upload_file(
                file_data=file_data,
                object_name=object_name,
                namespace="media",
                content_type=None,
            )

    async def test_init_storage(self) -> None:
        with patch.object(self.storage, "ensure_namespace_exists") as mock_ensure:
            mock_ensure.return_value = None
            await self.storage.init_storage()
            mock_ensure.assert_called_once_with(namespace="media")

    @patch("infra.s3.file_storages.settings")
    async def test_presign_put_object_returns_upload_and_access_urls(
        self,
        mock_settings: Mock,
    ) -> None:
        mock_settings.minio.presign_put_expires_seconds = 60
        mock_settings.get_minio_object_url.return_value = "http://localhost/media/test.txt"
        self.public_client.generate_presigned_url.return_value = "http://minio/upload"

        result = await self.storage.presign_put_object(
            object_name="test.txt",
            namespace="media",
            content_type="image/png",
        )

        assert result == PresignPutObject(
            upload_url="http://minio/upload",
            access_url="http://localhost/media/test.txt",
        )
        self.public_client.generate_presigned_url.assert_awaited_once_with(
            "put_object",
            Params={
                "Bucket": "media",
                "Key": "test.txt",
                "ContentType": "image/png",
            },
            ExpiresIn=60,
            HttpMethod="PUT",
        )
        mock_settings.get_minio_object_url.assert_called_once_with(
            bucket="media",
            object_path="test.txt",
        )
