from dataclasses import dataclass
from enum import StrEnum

from core.schemas import Secret


class RoleEnum(StrEnum):
    USER = "user"
    ADMIN = "admin"


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
