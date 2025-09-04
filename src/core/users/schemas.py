from dataclasses import dataclass

from core.enums import LabeledStrEnum
from core.schemas import Secret


class RoleEnum(LabeledStrEnum):
    USER = "user", "Пользователя"
    ADMIN = "admin", "Администратор"


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
