from typing import cast

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.files.file_name_generators import FileNameGenerator
from core.knowledge.files.clients import (
    KnowledgeFileClient,
    KnowledgeFileObjectCleaner,
    KnowledgeFileRollbackRegistrar,
    KnowledgePhotoProcessor,
)
from core.knowledge.files.enums import KnowledgeFileKind
from core.knowledge.files.schemas import KnowledgeFileRule, KnowledgeFileRules
from core.knowledge.files.services import KnowledgeFileCrudService
from core.knowledge.files.storages import KnowledgeFilesStorage
from core.knowledge.files.use_cases import KnowledgeFilesUseCase
from core.knowledge.items.storages import KnowledgeItemsStorage
from infra.config.constants import constants
from infra.files.processors import PersonPhotoContentProcessor
from infra.knowledge_file_actions import RequestKnowledgeFileRollbackRegistrar
from infra.post_commit_actions import RollbackActions
from infra.postgresql.storages.knowledge.files import KnowledgeFilesDatabaseStorage
from infra.s3.clients import S3ClientBundle, S3KnowledgeFileClient


class KnowledgeFilesProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_knowledge_photo_processor(self) -> KnowledgePhotoProcessor:
        return PersonPhotoContentProcessor(
            max_width_px=constants.knowledge_files.photo_max_width_px,
            max_height_px=constants.knowledge_files.photo_max_height_px,
            webp_quality=constants.knowledge_files.photo_webp_quality,
            webp_method=constants.knowledge_files.photo_webp_method,
        )

    @provide(scope=Scope.APP)
    async def provide_knowledge_file_client(
        self,
        s3_clients: S3ClientBundle,
    ) -> KnowledgeFileClient:
        return S3KnowledgeFileClient(
            internal_client=s3_clients.internal,
            bucket_name=constants.minio_buckets.knowledge_private,
            stream_chunk_size_bytes=constants.knowledge_files.stream_chunk_size_bytes,
        )

    @provide(scope=Scope.APP)
    async def provide_knowledge_file_object_cleaner(
        self,
        client: KnowledgeFileClient,
    ) -> KnowledgeFileObjectCleaner:
        return cast("KnowledgeFileObjectCleaner", client)

    @provide(scope=Scope.REQUEST)
    async def provide_knowledge_file_rollback_registrar(
        self,
        object_cleaner: KnowledgeFileObjectCleaner,
        rollback_actions: RollbackActions,
    ) -> KnowledgeFileRollbackRegistrar:
        return RequestKnowledgeFileRollbackRegistrar(
            object_cleaner=object_cleaner,
            rollback_actions=rollback_actions,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_knowledge_files_storage(
        self,
        session: AsyncSession,
    ) -> KnowledgeFilesStorage:
        return KnowledgeFilesDatabaseStorage(session=session)

    @provide(scope=Scope.REQUEST)
    async def provide_knowledge_file_crud_service(
        self,
        storage: KnowledgeFilesStorage,
        client: KnowledgeFileClient,
        photo_processor: KnowledgePhotoProcessor,
        file_name_generator: FileNameGenerator,
    ) -> KnowledgeFileCrudService:
        return KnowledgeFileCrudService(
            storage=storage,
            client=client,
            photo_processor=photo_processor,
            file_name_generator=file_name_generator,
            config=KnowledgeFileRules(
                values={
                    KnowledgeFileKind.ATTACHMENT: KnowledgeFileRule(
                        folder=constants.knowledge_files.attachment_folder,
                        allowed_mime_types=constants.knowledge_files.attachment_mime_types,
                        max_size_bytes=constants.knowledge_files.attachment_max_size_bytes,
                        original_name_max_length=(
                            constants.knowledge_files.original_name_max_length
                        ),
                        mime_type_max_length=constants.knowledge_files.mime_type_max_length,
                    ),
                    KnowledgeFileKind.PERSON_PHOTO: KnowledgeFileRule(
                        folder=constants.knowledge_files.person_photo_folder,
                        allowed_mime_types=constants.knowledge_files.photo_mime_types,
                        max_size_bytes=constants.knowledge_files.photo_max_size_bytes,
                        original_name_max_length=(
                            constants.knowledge_files.original_name_max_length
                        ),
                        mime_type_max_length=constants.knowledge_files.mime_type_max_length,
                    ),
                },
            ),
        )

    @provide(scope=Scope.REQUEST)
    async def provide_knowledge_files_use_case(
        self,
        item_storage: KnowledgeItemsStorage,
        file_storage: KnowledgeFilesStorage,
        file_service: KnowledgeFileCrudService,
    ) -> KnowledgeFilesUseCase:
        return KnowledgeFilesUseCase(
            item_storage=item_storage,
            file_storage=file_storage,
            file_service=file_service,
        )
