from dataclasses import dataclass
from datetime import datetime
from typing import Any

from core.auth.enums import RoleEnum
from core.auth.types import SessionSecret, SessionSecretHash, Token
from core.schemas import Secret


@dataclass(frozen=True, slots=True, kw_only=True)
class TokenPayloadValidationResult:
    is_valid: bool
    message: str


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseUser:
    username: str
    role: RoleEnum

    @property
    def is_anon(self) -> bool:
        return self.role == RoleEnum.ANON

    @property
    def is_owner(self) -> bool:
        return self.role == RoleEnum.OWNER

    @property
    def is_admin(self) -> bool:
        return self.role == RoleEnum.ADMIN

    @property
    def is_moderator(self) -> bool:
        return self.role == RoleEnum.MODERATOR

    @property
    def is_user(self) -> bool:
        return self.role == RoleEnum.USER

    @property
    def can_manage_content(self) -> bool:
        return self.role in {RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.MODERATOR}

    @property
    def can_manage_team(self) -> bool:
        return self.role in {RoleEnum.OWNER, RoleEnum.ADMIN}

    def has_role(self, role: RoleEnum) -> bool:
        if self.role == RoleEnum.OWNER:
            return True
        if self.role == RoleEnum.ADMIN:
            return role in {RoleEnum.ANON, RoleEnum.USER, RoleEnum.MODERATOR, RoleEnum.ADMIN}
        if self.role == RoleEnum.MODERATOR:
            return role in {RoleEnum.ANON, RoleEnum.USER, RoleEnum.MODERATOR}
        if self.role == RoleEnum.USER:
            return role in {RoleEnum.ANON, RoleEnum.USER}
        return self.role == role


@dataclass(frozen=True, slots=True, kw_only=True)
class User(BaseUser):
    password_hash: Secret[str]
    is_active: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class JwtUser(BaseUser):
    def to_dict(self) -> dict[str, Any]:
        return {"username": self.username, "role": self.role.value}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> JwtUser:
        return cls(
            username=payload["username"],
            role=RoleEnum.from_value(payload["role"]),
        )

    @classmethod
    def from_user(cls, user: User) -> JwtUser:
        return cls(
            username=user.username,
            role=user.role,
        )

    @classmethod
    def anonymous(cls) -> JwtUser:
        return cls(username="anonymous", role=RoleEnum.ANON)


@dataclass(frozen=True, slots=True, kw_only=True)
class AccessTokenPayload:
    username: str
    session_id: str

    def to_dict(self) -> dict[str, Any]:
        return {"username": self.username, "session_id": self.session_id}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> AccessTokenPayload:
        return cls(
            username=payload["username"],
            session_id=payload["session_id"],
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class AccessTokenResult:
    token: Token
    expires_in_seconds: int


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionCredentials:
    secret: SessionSecret
    expires_in_seconds: int


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthLoginResult:
    access_token: AccessTokenResult
    session: AuthSessionCredentials


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthRefreshAccessTokenResult:
    access_token: AccessTokenResult
    session: AuthSessionCredentials


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthUseCaseConfig:
    access_token_expires_in_seconds: int
    session_expires_in_seconds: int


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthLoginParams:
    username: str
    password: str
    required_role: RoleEnum
    current_datetime: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthAuthenticateParams:
    token: Token
    required_role: RoleEnum
    current_datetime: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthRefreshAccessTokenParams:
    session_secret: SessionSecret
    required_role: RoleEnum
    current_datetime: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthLogoutParams:
    token: Token
    session_secret: SessionSecret | None


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionCreate:
    username: str
    secret_hash: SessionSecretHash
    expires_at: datetime
    is_revoked: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSession:
    id: str
    username: str
    secret_hash: SessionSecretHash
    expires_at: datetime
    is_revoked: bool

    def is_active_at(self, *, now: datetime) -> bool:
        return not self.is_revoked and self.expires_at > now
