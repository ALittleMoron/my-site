from dataclasses import dataclass

from core.schemas import Secret
from core.users.enums import RoleEnum


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
