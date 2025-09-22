from dataclasses import dataclass
from typing import Any

from core.auth.enums import RoleEnum
from core.schemas import Secret


@dataclass(frozen=True, slots=True, kw_only=True)
class User:
    username: str
    password_hash: Secret[str]
    role: RoleEnum

    @property
    def is_admin(self) -> bool:
        return self.role == RoleEnum.ADMIN

    @property
    def is_user(self) -> bool:
        return self.role == RoleEnum.USER


@dataclass(kw_only=True)
class AuthTokenPayload:
    username: str
    role: RoleEnum

    def to_dict(self) -> dict[str, Any]:
        return {"username": self.username, "role": self.role.value}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AuthTokenPayload":
        return cls(
            username=payload["username"],
            role=RoleEnum(payload["role"]),
        )
