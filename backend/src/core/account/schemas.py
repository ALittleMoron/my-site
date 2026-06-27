from dataclasses import dataclass
from math import ceil
from typing import Self

from core.account.enums import ManagedAccountActionEnum
from core.account.exceptions import SelfAccountActionForbiddenError
from core.auth.enums import RoleEnum
from core.schemas import Secret, ValuedDataclass

SELF_FORBIDDEN_MANAGED_ACCOUNT_ACTIONS = (
    ManagedAccountActionEnum.UPDATE_ROLE,
    ManagedAccountActionEnum.ACTIVATE,
    ManagedAccountActionEnum.DEACTIVATE,
    ManagedAccountActionEnum.DELETE,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ManagedAccount:
    username: str
    role: RoleEnum
    is_active: bool

    @property
    def is_active_admin(self) -> bool:
        return self.is_active and self.role == RoleEnum.ADMIN

    def ensure_can_manage_account(
        self,
        *,
        target: Self,
        action: ManagedAccountActionEnum,
    ) -> None:
        if (
            action in SELF_FORBIDDEN_MANAGED_ACCOUNT_ACTIONS
            and self.username.casefold() == target.username.casefold()
        ):
            raise SelfAccountActionForbiddenError


@dataclass(frozen=True, slots=True, kw_only=True)
class ManagedAccounts(ValuedDataclass[ManagedAccount]):
    total_count: int
    total_pages: int

    @classmethod
    def from_page(
        cls,
        *,
        values: list[ManagedAccount],
        total_count: int,
        page_size: int,
    ) -> Self:
        return cls(
            values=values,
            total_count=total_count,
            total_pages=ceil(total_count / page_size) if total_count > 0 else 0,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ManagedAccountFilters:
    page: int
    page_size: int

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True, slots=True, kw_only=True)
class ManagedAccountCreateParams:
    username: str
    role: RoleEnum
    password: Secret[str]
    is_active: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class ManagedAccountRoleUpdateParams:
    role: RoleEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class ManagedAccountPasswordUpdateParams:
    password: Secret[str]
