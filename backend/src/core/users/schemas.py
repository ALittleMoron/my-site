from dataclasses import dataclass
from enum import StrEnum

from core.schemas import Secret


class RoleEnum(StrEnum):
    USER = "user"
    ADMIN = "admin"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(key.value, key.name) for key in cls]


@dataclass(frozen=True, slots=True, kw_only=True)
class User:
    username: str
    password: Secret[str]
    role: RoleEnum

    @property
    def is_admin(self) -> bool:
        return self.role == RoleEnum.ADMIN

    @property
    def is_user(self) -> bool:
        return self.role == RoleEnum.USER
