from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.knowledge.exceptions import (
    KnowledgeConflictError,
    KnowledgeFileNotFoundError,
)
from core.knowledge.files.schemas import KnowledgeFile
from core.knowledge.files.storages import KnowledgeFilesStorage
from infra.postgresql.models.knowledge.files import KnowledgeFileModel


@dataclass(kw_only=True)
class KnowledgeFilesDatabaseStorage(KnowledgeFilesStorage):
    session: AsyncSession

    async def list_item_files(
        self,
        *,
        item_id: str,
        author_username: str,
    ) -> list[KnowledgeFile]:
        query = (
            select(KnowledgeFileModel)
            .where(
                KnowledgeFileModel.item_id == item_id,
                KnowledgeFileModel.author_username == author_username,
            )
            .order_by(KnowledgeFileModel.kind, KnowledgeFileModel.created_at, KnowledgeFileModel.id)
        )
        return [model.to_domain_schema() for model in await self.session.scalars(query)]

    async def list_files_for_items(
        self,
        *,
        item_ids: set[str],
        author_username: str,
    ) -> list[KnowledgeFile]:
        if not item_ids:
            return []
        query = (
            select(KnowledgeFileModel)
            .where(
                KnowledgeFileModel.item_id.in_(item_ids),
                KnowledgeFileModel.author_username == author_username,
            )
            .order_by(
                KnowledgeFileModel.item_id,
                KnowledgeFileModel.kind,
                KnowledgeFileModel.created_at,
                KnowledgeFileModel.id,
            )
        )
        return [model.to_domain_schema() for model in await self.session.scalars(query)]

    async def get_file(self, *, file_id: str, author_username: str) -> KnowledgeFile:
        query = select(KnowledgeFileModel).where(
            KnowledgeFileModel.id == file_id,
            KnowledgeFileModel.author_username == author_username,
        )
        model = await self.session.scalar(query)
        if model is None:
            raise KnowledgeFileNotFoundError
        return model.to_domain_schema()

    async def create_file(self, *, file: KnowledgeFile) -> KnowledgeFile:
        model = KnowledgeFileModel.from_domain_schema(file=file)
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError as error:
            raise KnowledgeConflictError from error
        await self.session.refresh(model)
        return model.to_domain_schema()

    async def update_file_name(
        self,
        *,
        file: KnowledgeFile,
        name: str,
        updated_at: datetime,
    ) -> KnowledgeFile:
        query = (
            update(KnowledgeFileModel)
            .where(
                KnowledgeFileModel.id == file.id,
                KnowledgeFileModel.author_username == file.author_username,
            )
            .values(name=name, updated_at=updated_at)
            .returning(KnowledgeFileModel)
        )
        model = await self.session.scalar(query)
        if model is None:
            raise KnowledgeFileNotFoundError
        return model.to_domain_schema()

    async def delete_file(self, *, file: KnowledgeFile) -> None:
        query = (
            delete(KnowledgeFileModel)
            .where(
                KnowledgeFileModel.id == file.id,
                KnowledgeFileModel.author_username == file.author_username,
            )
            .returning(KnowledgeFileModel.id)
        )
        if await self.session.scalar(query) is None:
            raise KnowledgeFileNotFoundError
