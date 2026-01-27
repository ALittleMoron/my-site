from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_dev_utils.mixins.general import BetterReprMixin, TableNameMixin


class BaseModel(BetterReprMixin, TableNameMixin, DeclarativeBase):
    __abstract__ = True
    __join_application_prefix__ = True
    __table_name_delimiter__ = "__"
