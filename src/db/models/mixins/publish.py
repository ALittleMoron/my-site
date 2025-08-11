from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.decl_api import declarative_mixin

from core.enums import StatusEnum
from db.models import Base


@declarative_mixin
class PublishMixin(Base):
    __abstract__ = True

    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, native_enum=False, length=10),
        doc="Статус опубликования записи",
    )
