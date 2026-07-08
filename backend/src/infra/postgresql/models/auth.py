from datetime import datetime
from typing import Self

from sqlalchemy import Boolean, Enum, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_dev_utils.mixins.audit import AuditMixin
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

from core.account.schemas import ManagedAccount
from core.auth.enums import RoleEnum
from core.auth.schemas import AuthSession, User
from core.auth.types import SessionSecretHash
from core.schemas import Secret
from infra.postgresql.models.base import BaseModel
from infra.postgresql.models.mixins.ids import HexUuidIDMixin


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
        Enum(RoleEnum, native_enum=True, name="role_enum"),
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
        Index(
            "users_single_owner_uniq",
            role,
            unique=True,
            postgresql_where=role == RoleEnum.OWNER,
        ),
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


class AuthSessionModel(HexUuidIDMixin, AuditMixin, BaseModel):
    username: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("auth__user_model.username", ondelete="CASCADE"),
        doc="Username owning this server-side auth session",
    )
    secret_hash: Mapped[str] = mapped_column(
        String(length=64),
        doc="SHA-256 hash of the browser session secret",
    )
    expires_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True),
        doc="Absolute session expiration timestamp",
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        doc="Whether this auth session was explicitly revoked",
    )

    __table_args__ = (
        UniqueConstraint("secret_hash", name="auth_sessions_secret_hash_uniq"),
        Index(
            "auth_sessions_username_lower_active_expiry_idx",
            func.lower(username).label("username_lower"),
            is_revoked,
            expires_at,
        ),
        Index("auth_sessions_expiry_idx", expires_at),
    )

    @classmethod
    def from_domain_schema(cls, schema: AuthSession) -> Self:
        return cls(
            id=schema.id,
            username=schema.username,
            secret_hash=schema.secret_hash,
            expires_at=schema.expires_at,
            is_revoked=schema.is_revoked,
        )

    def to_domain_schema(self) -> AuthSession:
        return AuthSession(
            id=self.id,
            username=self.username,
            secret_hash=SessionSecretHash(self.secret_hash),
            expires_at=self.expires_at,
            is_revoked=self.is_revoked,
        )
