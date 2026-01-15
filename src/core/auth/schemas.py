from dataclasses import dataclass
from typing import Any

from core.auth.enums import RoleEnum
from core.schemas import Secret


@dataclass(frozen=True, slots=True, kw_only=True)
class Token:
    value: bytes


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseUser:
    username: str
    role: RoleEnum

    @property
    def is_admin(self) -> bool:
        return self.role == RoleEnum.ADMIN

    @property
    def is_user(self) -> bool:
        return self.role == RoleEnum.USER

    def has_role(self, role: RoleEnum) -> bool:
        if self.role == RoleEnum.ADMIN:
            return True
        return self.role == role


@dataclass(frozen=True, slots=True, kw_only=True)
class User(BaseUser):
    password_hash: Secret[str]


@dataclass(frozen=True, slots=True, kw_only=True)
class JwtUser(BaseUser):
    def to_dict(self) -> dict[str, Any]:
        return {"username": self.username, "role": self.role.value}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "JwtUser":
        return cls(
            username=payload["username"],
            role=RoleEnum(payload["role"]),
        )

    @classmethod
    def from_user(cls, user: User) -> "JwtUser":
        return cls(
            username=user.username,
            role=user.role,
        )
