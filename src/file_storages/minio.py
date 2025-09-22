import json
from dataclasses import dataclass
from io import BytesIO
from typing import Any

from miniopy_async.api import Minio
from miniopy_async.error import MinioException
from structlog import get_logger

from config.settings import settings
from core.file_storages.exceptions import FileStorageInternalError
from core.file_storages.schemas import FileUploadResult
from core.file_storages.storages import FileStorage

logger = get_logger(__name__)


@dataclass(kw_only=True)
class MinioFileStorage(FileStorage):
    client: Minio

    @staticmethod
    def create_bucket_policy(bucket_name: str) -> dict[str, Any]:
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                    "Resource": f"arn:aws:s3:::{bucket_name}",
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                },
            ],
        }

    async def ensure_namespace_exists(self, namespace: str) -> None:
        logger.info("Ensuring bucket exists", bucket_name=namespace)
        if not await self.client.bucket_exists(namespace):
            await self.client.make_bucket(bucket_name=namespace)
            logger.info("Bucket created", bucket_name=namespace)
        await self.client.set_bucket_policy(
            bucket_name=namespace,
            policy=json.dumps(self.create_bucket_policy(bucket_name=namespace)),
        )
        logger.info("Bucket policy set", bucket_name=namespace)

    async def upload_static_file(
        self,
        file_data: BytesIO,
        object_name: str,
        content_type: str | None = None,
    ) -> FileUploadResult:
        logger.info("Uploading file", bucket_name="static", object_name=object_name)
        try:
            await self.ensure_namespace_exists(namespace="static")
            result = await self.client.put_object(
                bucket_name="static",
                object_name=object_name,
                data=file_data,
                content_type=content_type or "application/octet-stream",
                length=file_data.getbuffer().nbytes,
            )
            file_url = settings.get_minio_object_url(bucket="static", object_path=object_name)
            upload_result = FileUploadResult(
                url=file_url,
                bucket="static",
                object_name=object_name,
                size=getattr(result, "size", 0),
            )
        except MinioException as e:
            logger.exception(
                "Minio upload failed",
                bucket_name="static",
                object_name=object_name,
            )
            raise FileStorageInternalError(message="File upload failed") from e
        else:
            logger.info(
                "File uploaded successfully",
                result=upload_result,
            )
            return upload_result

    async def init_storage(self) -> None:
        logger.info("Initializing storage")
        for bucket_name in ["static", "media"]:
            await self.ensure_namespace_exists(namespace=bucket_name)
        logger.info("Storage initialized successfully")
