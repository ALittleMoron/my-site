from typing import Self

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_dev_utils.mixins.audit import AuditMixin

from core.knowledge.files.enums import KnowledgeFileKind
from core.knowledge.files.schemas import KnowledgeFile
from infra.postgresql.models.base import BaseModel
from infra.postgresql.models.mixins.ids import HexUuidIDMixin


class KnowledgeFileModel(HexUuidIDMixin, AuditMixin, BaseModel):
    __tablename__ = "knowledge__knowledge_file_model"

    item_id: Mapped[str] = mapped_column(String(length=32))
    author_username: Mapped[str] = mapped_column(String(length=255))
    kind: Mapped[KnowledgeFileKind] = mapped_column(
        Enum(KnowledgeFileKind, native_enum=True, name="knowledge_file_kind_enum"),
    )
    relative_path: Mapped[str] = mapped_column(String(length=1024), unique=True)
    mime_type: Mapped[str] = mapped_column(String(length=255))
    size_bytes: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(length=255))
    original_name: Mapped[str] = mapped_column(String(length=255))
    original_sha256: Mapped[str] = mapped_column(String(length=64))

    __table_args__ = (
        UniqueConstraint("id", "author_username", name="knowledge_files_id_author_uniq"),
        ForeignKeyConstraint(
            ["item_id", "author_username"],
            [
                "knowledge__knowledge_item_model.id",
                "knowledge__knowledge_item_model.author_username",
            ],
            ondelete="CASCADE",
            name="knowledge_files_item_author_fk",
        ),
        Index(
            "knowledge_files_author_item_kind_id_idx",
            "author_username",
            "item_id",
            "kind",
            "id",
        ),
        Index(
            "knowledge_files_one_person_photo_idx",
            "item_id",
            unique=True,
            postgresql_where=kind == KnowledgeFileKind.PERSON_PHOTO,
        ),
        CheckConstraint(
            "size_bytes >= 0",
            name="knowledge_files_non_negative_size_check",
        ),
        CheckConstraint(
            "char_length(trim(name)) > 0 AND char_length(trim(original_name)) > 0",
            name="knowledge_files_names_check",
        ),
        CheckConstraint(
            "char_length(original_sha256) = 64",
            name="knowledge_files_sha256_length_check",
        ),
    )

    @classmethod
    def from_domain_schema(cls, *, file: KnowledgeFile) -> Self:
        return cls(
            id=file.id,
            item_id=file.item_id,
            author_username=file.author_username,
            kind=file.kind,
            relative_path=file.relative_path,
            mime_type=file.mime_type,
            size_bytes=file.size_bytes,
            name=file.name,
            original_name=file.original_name,
            original_sha256=file.original_sha256,
            created_at=file.created_at,
            updated_at=file.updated_at,
        )

    def to_domain_schema(self) -> KnowledgeFile:
        return KnowledgeFile(
            id=self.id,
            item_id=self.item_id,
            author_username=self.author_username,
            kind=self.kind,
            relative_path=self.relative_path,
            mime_type=self.mime_type,
            size_bytes=self.size_bytes,
            name=self.name,
            original_name=self.original_name,
            original_sha256=self.original_sha256,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
