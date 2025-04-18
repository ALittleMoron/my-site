from sqlalchemy_dev_utils.mixins.ids import IntegerIDMixin

from db.models import Base


class AuditModel(Base, IntegerIDMixin):
    event_type: Mapped[]
