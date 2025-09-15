from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_dev_utils.mixins.ids import UUIDMixin

from core.contacts.schemas import ContactMe
from db.models.base import Base


class ContactMeModel(Base, UUIDMixin):
    __tablename__ = "mentoring_contact_me"

    user_ip: Mapped[str] = mapped_column(String(length=45))
    name: Mapped[str | None] = mapped_column(String(length=255))
    email: Mapped[str | None] = mapped_column(String(length=255))
    telegram: Mapped[str | None] = mapped_column(String(length=256))
    message: Mapped[str] = mapped_column()

    @classmethod
    def from_schema(cls, form: ContactMe) -> "ContactMeModel":
        return cls(
            id=form.id,
            user_ip=form.user_ip,
            name=form.name,
            email=form.email,
            telegram=form.telegram,
            message=form.message,
        )

    def to_schema(self) -> ContactMe:
        return ContactMe(
            id=self.id,
            user_ip=self.user_ip,
            name=self.name,
            email=self.email,
            telegram=self.telegram,
            message=self.message,
        )
