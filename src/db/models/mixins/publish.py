from datetime import datetime

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.decl_api import declarative_mixin
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

from core.enums import PublishStatusEnum
from db.models import Base


@declarative_mixin
class PublishMixin(Base):
    __abstract__ = True

    published_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime(timezone=True),
        doc="Publication date of the blog post",
    )
    publish_status: Mapped[PublishStatusEnum] = mapped_column(
        Enum(PublishStatusEnum, native_enum=False, length=10),
        doc="Статус опубликования записи",
    )
