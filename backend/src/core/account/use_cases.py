from contextlib import suppress
from dataclasses import dataclass

from core.account.enums import ManagedAccountActionEnum
from core.account.exceptions import (
    AccountUsernameAlreadyExistsError,
    InvalidManagedAccountRoleError,
)
from core.account.schemas import (
    ManagedAccount,
    ManagedAccountCreateParams,
    ManagedAccountFilters,
    ManagedAccountPasswordUpdateParams,
    ManagedAccountRoleUpdateParams,
    ManagedAccounts,
)
from core.account.storages import ManagedAccountStorage
from core.auth.enums import RoleEnum
from core.auth.exceptions import UserNotFoundError
from core.auth.password_hashers import PasswordHasher


@dataclass(kw_only=True, slots=True, frozen=True)
class AccountsUseCase:
    storage: ManagedAccountStorage
    hasher: PasswordHasher

    async def list_accounts(self, *, filters: ManagedAccountFilters) -> ManagedAccounts:
        accounts, total_count = await self.storage.list_managed_accounts(filters=filters)
        return ManagedAccounts.from_page(
            values=accounts,
            total_count=total_count,
            page_size=filters.page_size,
        )

    async def get_account(self, *, username: str) -> ManagedAccount:
        return await self.storage.get_managed_account(username=username)

    async def create_account(
        self,
        *,
        params: ManagedAccountCreateParams,
        current_username: str,
    ) -> ManagedAccount:
        if params.role not in {RoleEnum.ADMIN, RoleEnum.MODERATOR}:
            raise InvalidManagedAccountRoleError
        current_account = await self.storage.get_managed_account(username=current_username)
        current_account.ensure_can_create_account_with_role(role=params.role)
        with suppress(UserNotFoundError):
            await self.storage.get_user_by_username(username=params.username)
            raise AccountUsernameAlreadyExistsError
        return await self.storage.create_managed_account(
            username=params.username,
            role=params.role,
            password_hash=self.hasher.hash_password(params.password.get_secret_value()),
            is_active=params.is_active,
        )

    async def update_role(
        self,
        *,
        username: str,
        params: ManagedAccountRoleUpdateParams,
        current_username: str,
    ) -> ManagedAccount:
        if params.role not in {RoleEnum.ADMIN, RoleEnum.MODERATOR}:
            raise InvalidManagedAccountRoleError
        target_account = await self.storage.get_managed_account(username=username)
        current_account = await self.storage.get_managed_account(username=current_username)
        current_account.ensure_can_update_account_role(target=target_account, role=params.role)
        return await self.storage.update_managed_account_role(
            username=username,
            role=params.role,
        )

    async def update_password(
        self,
        *,
        username: str,
        params: ManagedAccountPasswordUpdateParams,
        current_username: str,
    ) -> ManagedAccount:
        target_account = await self.storage.get_managed_account(username=username)
        current_account = await self.storage.get_managed_account(username=current_username)
        current_account.ensure_can_manage_account(
            target=target_account,
            action=ManagedAccountActionEnum.UPDATE_PASSWORD,
        )
        return await self.storage.update_managed_account_password(
            username=username,
            password_hash=self.hasher.hash_password(params.password.get_secret_value()),
        )

    async def activate_account(self, *, username: str, current_username: str) -> ManagedAccount:
        target_account = await self.storage.get_managed_account(username=username)
        current_account = await self.storage.get_managed_account(username=current_username)
        current_account.ensure_can_manage_account(
            target=target_account,
            action=ManagedAccountActionEnum.ACTIVATE,
        )
        return await self.storage.activate_managed_account(username=username)

    async def deactivate_account(self, *, username: str, current_username: str) -> ManagedAccount:
        target_account = await self.storage.get_managed_account(username=username)
        current_account = await self.storage.get_managed_account(username=current_username)
        current_account.ensure_can_manage_account(
            target=target_account,
            action=ManagedAccountActionEnum.DEACTIVATE,
        )
        return await self.storage.deactivate_managed_account(username=username)

    async def delete_account(self, *, username: str, current_username: str) -> None:
        target_account = await self.storage.get_managed_account(username=username)
        current_account = await self.storage.get_managed_account(username=current_username)
        current_account.ensure_can_manage_account(
            target=target_account,
            action=ManagedAccountActionEnum.DELETE,
        )
        await self.storage.delete_managed_account(username=username)
