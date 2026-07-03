from typing import Self

from sqlalchemy import Enum, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_dev_utils.mixins.audit import AuditMixin

from core.files.enums import FilePurpose
from core.files.schemas import StoredFile
from core.files.types import Namespace
from infra.postgresql.models.base import BaseModel
from infra.postgresql.models.mixins.ids import HexUuidIDMixin


class FileModel(HexUuidIDMixin, AuditMixin, BaseModel):
    purpose: Mapped[FilePurpose] = mapped_column(
        Enum(
            FilePurpose,
            native_enum=True,
            name="file_purpose_enum",
        ),
        doc="Business purpose that controls file validation and storage folder",
    )
    namespace: Mapped[Namespace] = mapped_column(
        String(length=63),
        doc="Object storage namespace or bucket",
    )
    relative_path: Mapped[str] = mapped_column(
        String(length=2048),
        doc="Object path relative to namespace",
    )
    mime_type: Mapped[str] = mapped_column(
        String(length=255),
        doc="Uploaded file MIME type",
    )
    size_bytes: Mapped[int] = mapped_column(
        doc="Uploaded file size in bytes",
    )
    name: Mapped[str] = mapped_column(
        String(length=255),
        doc="Display name",
    )
    original_name: Mapped[str] = mapped_column(
        String(length=255),
        doc="Original uploaded file name",
    )

    __table_args__ = (
        UniqueConstraint(
            "namespace",
            "relative_path",
            name="files_file_namespace_relative_path_uniq",
        ),
        Index("files_file_purpose_created_id_idx", "purpose", "created_at", "id"),
    )

    @classmethod
    def from_domain_schema(cls, file: StoredFile) -> Self:
        return cls(
            id=file.id,
            purpose=file.purpose,
            namespace=file.namespace,
            relative_path=file.relative_path,
            mime_type=file.mime_type,
            size_bytes=file.size_bytes,
            name=file.name,
            original_name=file.original_name,
            created_at=file.created_at,
            updated_at=file.updated_at,
        )

    def to_domain_schema(self) -> StoredFile:
        return StoredFile(
            id=self.id,
            purpose=self.purpose,
            namespace=self.namespace,
            relative_path=self.relative_path,
            mime_type=self.mime_type,
            size_bytes=self.size_bytes,
            name=self.name,
            original_name=self.original_name,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
