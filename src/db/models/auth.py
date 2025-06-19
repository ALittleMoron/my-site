from sqlalchemy import Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from core.schemas import Secret
from core.users.schemas import RoleEnum, User
from db.models.base import Base


class UserModel(Base):
    """Пользователь."""

    username: Mapped[str] = mapped_column(
        String(255),
        doc="Имя пользователя",
        primary_key=True,
    )
    password: Mapped[str] = mapped_column(
        String(127),
        doc="Зашифрованный парользо пользователя",
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, native_enum=False, length=10),
        doc="Роль пользователя",
    )

    __tablename__ = "users"
    __table_args__ = (Index("users_username_idx", username),)

    def to_domain_schema(self) -> User:
        return User(
            username=self.username,
            password=Secret(self.password),
            role=self.role,
        )

    @classmethod
    def from_domain_schema(cls, schema: User) -> "UserModel":
        return cls(
            username=schema.username,
            password=schema.password.get_secret_value(),
            role=schema.role,
        )
