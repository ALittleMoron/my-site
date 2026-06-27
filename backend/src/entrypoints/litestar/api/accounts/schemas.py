from typing import Annotated, Self, cast

from pydantic import Field, field_validator

from core.account.schemas import (
    ManagedAccount,
    ManagedAccountCreateParams,
    ManagedAccountPasswordUpdateParams,
    ManagedAccountRoleUpdateParams,
    ManagedAccounts,
)
from core.auth.enums import RoleEnum
from core.schemas import Secret
from entrypoints.litestar.api.schemas import CamelCaseSchema
from entrypoints.litestar.api.validation import AccountPasswordString, AccountUsernameString


class ManagedAccountRoleMixin(CamelCaseSchema):
    role: Annotated[RoleEnum, Field(title="Managed account role")]

    @field_validator("role")
    @classmethod
    def validate_managed_role(cls, value: RoleEnum) -> RoleEnum:
        if value not in {RoleEnum.ADMIN, RoleEnum.MODERATOR}:
            msg = "role must be admin or moderator"
            raise ValueError(msg)
        return value


class ManagedAccountCreateRequestSchema(ManagedAccountRoleMixin):
    username: Annotated[AccountUsernameString, Field(title="Username")]
    password: Annotated[AccountPasswordString, Field(title="Password")]
    is_active: Annotated[bool, Field(title="Active")]

    def to_domain_schema(self) -> ManagedAccountCreateParams:
        return ManagedAccountCreateParams(
            username=self.username,
            role=self.role,
            password=Secret(self.password),
            is_active=self.is_active,
        )


class ManagedAccountRoleUpdateRequestSchema(ManagedAccountRoleMixin):
    def to_domain_schema(self) -> ManagedAccountRoleUpdateParams:
        return ManagedAccountRoleUpdateParams(role=self.role)


class ManagedAccountPasswordUpdateRequestSchema(CamelCaseSchema):
    password: Annotated[AccountPasswordString, Field(title="Password")]

    def to_domain_schema(self) -> ManagedAccountPasswordUpdateParams:
        return ManagedAccountPasswordUpdateParams(password=Secret(self.password))


class ManagedAccountResponseSchema(CamelCaseSchema):
    username: Annotated[str, Field(title="Username")]
    role: Annotated[RoleEnum, Field(title="Role")]
    is_active: Annotated[bool, Field(title="Active")]

    @classmethod
    def from_domain_schema(cls, *, schema: ManagedAccount) -> Self:
        return cast(
            "Self",
            cls.model_construct(
                username=schema.username,
                role=schema.role,
                is_active=schema.is_active,
            ),
        )


class ManagedAccountsResponseSchema(CamelCaseSchema):
    total_count: Annotated[int, Field(title="Total count")]
    total_pages: Annotated[int, Field(title="Total pages")]
    accounts: Annotated[list[ManagedAccountResponseSchema], Field(title="Accounts")]

    @classmethod
    def from_domain_schema(cls, *, schema: ManagedAccounts) -> Self:
        return cast(
            "Self",
            cls.model_construct(
                total_count=schema.total_count,
                total_pages=schema.total_pages,
                accounts=[
                    ManagedAccountResponseSchema.from_domain_schema(schema=account)
                    for account in schema.values
                ],
            ),
        )
