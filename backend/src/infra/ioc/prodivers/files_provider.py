import secrets
from collections.abc import AsyncIterable
from contextlib import AsyncExitStack
from typing import cast

from aiobotocore.config import AioConfig
from aiobotocore.session import get_session
from dishka import Provider, Scope, provide
from types_aiobotocore_s3.client import S3Client

from core.files.file_name_generators import FileNameGenerator, TimestampFileNameGenerator
from core.files.file_storages import FileStorage
from core.files.use_cases import FilesUseCase
from infra.config.constants import constants
from infra.config.settings import settings
from infra.s3.file_storages import S3ClientBundle, S3FileStorage


class FilesProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_file_name_generator(self) -> FileNameGenerator:
        return TimestampFileNameGenerator(
            random_suffix_length=4,
            random_generator=secrets.token_hex,
        )

    @provide(scope=Scope.APP)
    async def provide_s3_clients(self) -> AsyncIterable[S3ClientBundle]:
        session = get_session()
        config = AioConfig(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        )
        client_options = {
            "region_name": settings.minio.region,
            "aws_access_key_id": settings.minio.access_key,
            "aws_secret_access_key": settings.minio.secret_key.get_secret_value(),
            "config": config,
        }
        async with AsyncExitStack() as exit_stack:
            internal_client = cast(
                "S3Client",
                await exit_stack.enter_async_context(
                    session.create_client(
                        "s3",
                        endpoint_url=settings.minio.internal_endpoint_url,
                        **client_options,
                    ),
                ),
            )
            public_client = cast(
                "S3Client",
                await exit_stack.enter_async_context(
                    session.create_client(
                        "s3",
                        endpoint_url=settings.minio.public_url.rstrip("/"),
                        **client_options,
                    ),
                ),
            )
            yield S3ClientBundle(
                internal=internal_client,
                public=public_client,
            )

    @provide(scope=Scope.APP)
    async def provide_file_storage(self, s3_clients: S3ClientBundle) -> FileStorage:
        return S3FileStorage(clients=s3_clients)

    @provide(scope=Scope.REQUEST)
    async def provide_files_use_case(
        self,
        file_storage: FileStorage,
        file_name_generator: FileNameGenerator,
    ) -> FilesUseCase:
        return FilesUseCase(
            file_storage=file_storage,
            file_name_generator=file_name_generator,
            allowed_upload_media_types=constants.files.allowed_to_upload_media_types,
        )
