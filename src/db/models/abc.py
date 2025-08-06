from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from core.enums import StatusEnum
from db.models.base import Base


class PublishModel(Base):
    __abstract__ = True

    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, native_enum=False, length=10),
        doc="Статус",
    )
