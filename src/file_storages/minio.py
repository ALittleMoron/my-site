import json
from dataclasses import dataclass
from datetime import timedelta
from io import BytesIO
from typing import Any

from miniopy_async.api import Minio
from miniopy_async.error import MinioException

from config.loggers import logger
from config.settings import settings
from core.files.exceptions import FileStorageInternalError, NamespaceNotAllowedError
from core.files.file_storages import FileStorage
from core.files.schemas import FileUploadResult
from core.files.types import Namespace


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

    @staticmethod
    def _ensure_valid_namespace(namespace: str) -> Namespace:
        if namespace not in {"static", "media"}:
            logger.error("Passed incorrect namespace:", bucket_name=namespace)
            raise NamespaceNotAllowedError(template_vars={"namespace": namespace})
        return namespace  # type: ignore[return-value]

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

    async def upload_file(
        self,
        file_data: BytesIO,
        object_name: str,
        namespace: str,
        content_type: str | None = None,
    ) -> FileUploadResult:
        _namespace = self._ensure_valid_namespace(namespace)
        logger.info("Uploading file", bucket_name=_namespace, object_name=object_name)
        try:
            await self.ensure_namespace_exists(namespace=_namespace)
            result = await self.client.put_object(
                bucket_name=_namespace,
                object_name=object_name,
                data=file_data,
                content_type=content_type or "application/octet-stream",
                length=file_data.getbuffer().nbytes,
            )
            file_url = settings.get_minio_object_url(bucket=_namespace, object_path=object_name)
            upload_result = FileUploadResult(
                url=file_url,
                bucket=_namespace,
                object_name=object_name,
                size=getattr(result, "size", 0),
            )
        except MinioException as e:
            logger.exception(
                "Minio upload failed",
                bucket_name=_namespace,
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

    async def presign_put_object(
        self,
        object_name: str,
        namespace: str,
    ) -> str:
        _namespace = self._ensure_valid_namespace(namespace)
        return await self.client.presigned_put_object(
            bucket_name=_namespace,
            object_name=object_name,
            expires=timedelta(seconds=settings.minio.presign_put_expires_seconds),
        )
