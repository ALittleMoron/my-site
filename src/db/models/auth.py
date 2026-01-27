from sqlalchemy import Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from core.auth.enums import RoleEnum
from core.auth.schemas import User
from core.schemas import Secret
from db.models.base import BaseModel


class UserModel(BaseModel):
    username: Mapped[str] = mapped_column(
        String(255),
        doc="Имя пользователя",
        primary_key=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(127),
        doc="Зашифрованный парользо пользователя",
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, native_enum=False, length=10, name="role_enum"),
        doc="Роль пользователя",
    )

    __table_args__ = (Index("users_username_idx", username),)

    def to_domain_schema(self) -> User:
        return User(
            username=self.username,
            password_hash=Secret(self.password_hash),
            role=self.role,
        )

    @classmethod
    def from_domain_schema(cls, schema: User) -> UserModel:
        return cls(
            username=schema.username,
            password_hash=schema.password_hash.get_secret_value(),
            role=schema.role,
        )
