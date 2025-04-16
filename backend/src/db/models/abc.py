from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from core.competency_matrix.enums import StatusEnum
from db.models.base import Base


class PublishModel(Base):
    __abstract__ = True

    status: Mapped[str] = mapped_column(
        Enum(StatusEnum, native_enum=False, length=10),
        doc="Статус",
    )
