from contextlib import suppress
from dataclasses import dataclass

from core.account.enums import ManagedAccountActionEnum
from core.account.exceptions import (
    AccountUsernameAlreadyExistsError,
    InvalidManagedAccountRoleError,
)
from core.account.schemas import (
    ManagedAccount,
    ManagedAccountCreateOperationParams,
    ManagedAccountFilters,
    ManagedAccountPasswordUpdateOperationParams,
    ManagedAccountRoleUpdateOperationParams,
    ManagedAccounts,
    ManagedAccountTargetOperationParams,
)
from core.account.storages import ManagedAccountStorage
from core.auth.enums import RoleEnum
from core.auth.exceptions import UserNotFoundError
from core.auth.password_hashers import PasswordHasher
from core.auth.storages import AuthSessionStorage


@dataclass(kw_only=True, slots=True, frozen=True)
class AccountsUseCase:
    storage: ManagedAccountStorage
    hasher: PasswordHasher
    auth_session_storage: AuthSessionStorage

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
        params: ManagedAccountCreateOperationParams,
    ) -> ManagedAccount:
        create_params = params.create_params
        if create_params.role not in {RoleEnum.ADMIN, RoleEnum.MODERATOR}:
            raise InvalidManagedAccountRoleError
        current_account = await self.storage.get_managed_account(username=params.current_username)
        current_account.ensure_can_create_account_with_role(role=create_params.role)
        with suppress(UserNotFoundError):
            await self.storage.get_user_by_username(username=create_params.username)
            raise AccountUsernameAlreadyExistsError
        return await self.storage.create_managed_account(
            username=create_params.username,
            role=create_params.role,
            password_hash=self.hasher.hash_password(create_params.password.get_secret_value()),
            is_active=create_params.is_active,
        )

    async def update_role(
        self,
        *,
        params: ManagedAccountRoleUpdateOperationParams,
    ) -> ManagedAccount:
        role_params = params.role_params
        if role_params.role not in {RoleEnum.ADMIN, RoleEnum.MODERATOR}:
            raise InvalidManagedAccountRoleError
        target_account = await self.storage.get_managed_account(username=params.target_username)
        current_account = await self.storage.get_managed_account(username=params.current_username)
        current_account.ensure_can_update_account_role(target=target_account, role=role_params.role)
        return await self.storage.update_managed_account_role(
            username=params.target_username,
            role=role_params.role,
        )

    async def update_password(
        self,
        *,
        params: ManagedAccountPasswordUpdateOperationParams,
    ) -> ManagedAccount:
        password_params = params.password_params
        target_account = await self.storage.get_managed_account(username=params.target_username)
        current_account = await self.storage.get_managed_account(username=params.current_username)
        current_account.ensure_can_manage_account(
            target=target_account,
            action=ManagedAccountActionEnum.UPDATE_PASSWORD,
        )
        account = await self.storage.update_managed_account_password(
            username=params.target_username,
            password_hash=self.hasher.hash_password(password_params.password.get_secret_value()),
        )
        await self.auth_session_storage.revoke_user_sessions(username=params.target_username)
        return account

    async def activate_account(
        self,
        *,
        params: ManagedAccountTargetOperationParams,
    ) -> ManagedAccount:
        target_account = await self.storage.get_managed_account(username=params.target_username)
        current_account = await self.storage.get_managed_account(username=params.current_username)
        current_account.ensure_can_manage_account(
            target=target_account,
            action=ManagedAccountActionEnum.ACTIVATE,
        )
        return await self.storage.activate_managed_account(username=params.target_username)

    async def deactivate_account(
        self,
        *,
        params: ManagedAccountTargetOperationParams,
    ) -> ManagedAccount:
        target_account = await self.storage.get_managed_account(username=params.target_username)
        current_account = await self.storage.get_managed_account(username=params.current_username)
        current_account.ensure_can_manage_account(
            target=target_account,
            action=ManagedAccountActionEnum.DEACTIVATE,
        )
        account = await self.storage.deactivate_managed_account(username=params.target_username)
        await self.auth_session_storage.revoke_user_sessions(username=params.target_username)
        return account

    async def delete_account(self, *, params: ManagedAccountTargetOperationParams) -> None:
        target_account = await self.storage.get_managed_account(username=params.target_username)
        current_account = await self.storage.get_managed_account(username=params.current_username)
        current_account.ensure_can_manage_account(
            target=target_account,
            action=ManagedAccountActionEnum.DELETE,
        )
        await self.storage.delete_managed_account(username=params.target_username)
        await self.auth_session_storage.revoke_user_sessions(username=params.target_username)
