from sqlalchemy import Boolean, Enum, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from core.account.schemas import ManagedAccount
from core.auth.enums import RoleEnum
from core.auth.schemas import User
from core.schemas import Secret
from infra.postgresql.models.base import BaseModel


class UserModel(BaseModel):
    username: Mapped[str] = mapped_column(
        String(255),
        doc="Username",
        primary_key=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(127),
        doc="User password hash",
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, native_enum=False, length=10, name="role_enum"),
        doc="User role",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        doc="Whether the user may authenticate",
    )

    __table_args__ = (
        Index("users_username_idx", username),
        Index(
            "users_username_lower_uniq",
            func.lower(username).label("username_lower"),
            unique=True,
        ),
        Index(
            "users_managed_accounts_list_idx",
            role,
            func.lower(username).label("username_lower"),
            username,
        ),
        Index("users_active_admins_idx", role, is_active),
    )

    def to_domain_schema(self) -> User:
        return User(
            username=self.username,
            password_hash=Secret(self.password_hash),
            role=self.role,
            is_active=self.is_active,
        )

    def to_managed_account_schema(self) -> ManagedAccount:
        return ManagedAccount(
            username=self.username,
            role=self.role,
            is_active=self.is_active,
        )

    @classmethod
    def from_domain_schema(cls, schema: User) -> UserModel:
        return cls(
            username=schema.username,
            password_hash=schema.password_hash.get_secret_value(),
            role=schema.role,
            is_active=schema.is_active,
        )
