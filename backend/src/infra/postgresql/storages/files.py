from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import delete, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import EntryNotFoundError
from core.files.enums import FilePurpose
from core.files.schemas import StoredFile, StoredFiles
from core.files.storages import FileStorage
from infra.postgresql.models import ArticleFileUsageModel, ArticleModel, FileModel


@dataclass(kw_only=True)
class FilesDatabaseStorage(FileStorage):
    session: AsyncSession

    async def create_file(self, file: StoredFile) -> StoredFile:
        file_model = FileModel.from_domain_schema(file)
        self.session.add(file_model)
        await self.session.flush()
        return file_model.to_domain_schema()

    async def get_file(self, file_id: str) -> StoredFile:
        file_model = await self.session.get(FileModel, file_id)
        if file_model is None:
            raise EntryNotFoundError
        return file_model.to_domain_schema()

    async def list_files(self, purpose: FilePurpose) -> StoredFiles:
        query = (
            select(FileModel)
            .where(FileModel.purpose == purpose)
            .order_by(FileModel.created_at.desc(), FileModel.id)
        )
        file_models = await self.session.scalars(query)
        return StoredFiles(
            values=[file_model.to_domain_schema() for file_model in file_models],
        )

    async def update_file_name(
        self,
        file_id: str,
        name: str,
        updated_at: datetime,
    ) -> StoredFile:
        query = (
            update(FileModel)
            .where(FileModel.id == file_id)
            .values(name=name, updated_at=updated_at)
            .returning(FileModel)
        )
        file_model = await self.session.scalar(query)
        if file_model is None:
            raise EntryNotFoundError
        return file_model.to_domain_schema()

    async def file_has_usages(self, file_id: str) -> bool:
        query = select(
            exists().where(ArticleModel.cover_image_file_id == file_id)
            | exists().where(ArticleFileUsageModel.file_id == file_id),
        )
        return bool(await self.session.scalar(query))

    async def delete_file(self, file_id: str) -> None:
        await self.session.execute(delete(FileModel).where(FileModel.id == file_id))
