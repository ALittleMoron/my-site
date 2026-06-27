from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.datastructures import State
from litestar.di import NamedDependency, Provide
from litestar.params import Body, FromPath

from core.account.schemas import ManagedAccountFilters
from core.account.use_cases import AccountsUseCase
from core.auth.schemas import JwtUser
from core.auth.types import Token
from entrypoints.litestar.api.accounts.dependencies import provide_managed_account_filters
from entrypoints.litestar.api.accounts.schemas import (
    ManagedAccountCreateRequestSchema,
    ManagedAccountPasswordUpdateRequestSchema,
    ManagedAccountResponseSchema,
    ManagedAccountRoleUpdateRequestSchema,
    ManagedAccountsResponseSchema,
)
from entrypoints.litestar.guards import team_manager_guard


class AdminAccountsApiController(Controller):
    path = "/accounts"
    tags = ["admin accounts"]
    guards = [team_manager_guard]

    @get(
        "",
        description="Get managed owner, admin and moderator accounts.",
        name="admin-accounts-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        dependencies={"filters": Provide(provide_managed_account_filters, sync_to_thread=False)},
    )
    async def list_accounts(
        self,
        use_case: FromDishka[AccountsUseCase],
        filters: NamedDependency[ManagedAccountFilters],
    ) -> ManagedAccountsResponseSchema:
        accounts = await use_case.list_accounts(filters=filters)
        return ManagedAccountsResponseSchema.from_domain_schema(schema=accounts)

    @post(
        "",
        description="Create a managed admin or moderator account.",
        name="admin-accounts-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_account(
        self,
        data: Annotated[ManagedAccountCreateRequestSchema, Body()],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AccountsUseCase],
    ) -> ManagedAccountResponseSchema:
        account = await use_case.create_account(
            params=data.to_domain_schema(),
            current_username=request.user.username,
        )
        return ManagedAccountResponseSchema.from_domain_schema(schema=account)

    @get(
        "/{username:str}",
        description="Get managed account details.",
        name="admin-accounts-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_account(
        self,
        username: FromPath[str],
        use_case: FromDishka[AccountsUseCase],
    ) -> ManagedAccountResponseSchema:
        account = await use_case.get_account(username=username)
        return ManagedAccountResponseSchema.from_domain_schema(schema=account)

    @put(
        "/{username:str}/role",
        description="Update a managed account role.",
        name="admin-accounts-role-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_role(
        self,
        username: FromPath[str],
        data: Annotated[ManagedAccountRoleUpdateRequestSchema, Body()],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AccountsUseCase],
    ) -> ManagedAccountResponseSchema:
        account = await use_case.update_role(
            username=username,
            params=data.to_domain_schema(),
            current_username=request.user.username,
        )
        return ManagedAccountResponseSchema.from_domain_schema(schema=account)

    @put(
        "/{username:str}/password",
        description="Update a managed account password.",
        name="admin-accounts-password-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_password(
        self,
        username: FromPath[str],
        data: Annotated[ManagedAccountPasswordUpdateRequestSchema, Body()],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AccountsUseCase],
    ) -> ManagedAccountResponseSchema:
        account = await use_case.update_password(
            username=username,
            params=data.to_domain_schema(),
            current_username=request.user.username,
        )
        return ManagedAccountResponseSchema.from_domain_schema(schema=account)

    @post(
        "/{username:str}/activate",
        description="Activate a managed account.",
        name="admin-accounts-activate-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def activate_account(
        self,
        username: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AccountsUseCase],
    ) -> ManagedAccountResponseSchema:
        account = await use_case.activate_account(
            username=username,
            current_username=request.user.username,
        )
        return ManagedAccountResponseSchema.from_domain_schema(schema=account)

    @post(
        "/{username:str}/deactivate",
        description="Deactivate a managed account.",
        name="admin-accounts-deactivate-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def deactivate_account(
        self,
        username: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AccountsUseCase],
    ) -> ManagedAccountResponseSchema:
        account = await use_case.deactivate_account(
            username=username,
            current_username=request.user.username,
        )
        return ManagedAccountResponseSchema.from_domain_schema(schema=account)

    @delete(
        "/{username:str}",
        description="Delete a managed account.",
        name="admin-accounts-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_account(
        self,
        username: FromPath[str],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AccountsUseCase],
    ) -> None:
        await use_case.delete_account(username=username, current_username=request.user.username)


admin_router = DishkaRouter("", route_handlers=[AdminAccountsApiController])
