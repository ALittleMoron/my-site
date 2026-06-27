import pytest_asyncio
from httpx import codes

from core.account.schemas import (
    ManagedAccount,
    ManagedAccountCreateParams,
    ManagedAccountFilters,
    ManagedAccountPasswordUpdateParams,
    ManagedAccountRoleUpdateParams,
)
from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser
from core.schemas import Secret
from tests.test_cases import ApiTestCase


class TestAdminAccountsAPI(ApiTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.authentication_use_case = await self.container.get_auth_use_case()
        self.use_case = await self.container.get_accounts_use_case()

    def test_list_accounts(self) -> None:
        self.use_case.list_accounts.return_value = self.factory.core.managed_accounts(
            values=[
                ManagedAccount(username="Owner", role=RoleEnum.OWNER, is_active=True),
                ManagedAccount(username="Admin", role=RoleEnum.ADMIN, is_active=True),
                ManagedAccount(username="Moderator", role=RoleEnum.MODERATOR, is_active=False),
            ],
            total_count=3,
            total_pages=1,
        )

        response = self.api.get_admin_accounts(page=2, page_size=10)

        self.asserts.status(response=response, expected_status=codes.OK)
        assert response.json() == {
            "totalCount": 3,
            "totalPages": 1,
            "accounts": [
                {"username": "Owner", "role": "owner", "isActive": True},
                {"username": "Admin", "role": "admin", "isActive": True},
                {"username": "Moderator", "role": "moderator", "isActive": False},
            ],
        }
        self.use_case.list_accounts.assert_called_once_with(
            filters=ManagedAccountFilters(page=2, page_size=10),
        )

    def test_create_account(self) -> None:
        self.use_case.create_account.return_value = ManagedAccount(
            username="Moderator_1",
            role=RoleEnum.MODERATOR,
            is_active=True,
        )

        response = self.api.post_create_admin_account(
            data={
                "username": "Moderator_1",
                "role": "moderator",
                "password": "password123",
                "isActive": True,
            },
        )

        self.asserts.status(response=response, expected_status=codes.CREATED)
        assert response.json() == {
            "username": "Moderator_1",
            "role": "moderator",
            "isActive": True,
        }
        self.use_case.create_account.assert_called_once_with(
            params=ManagedAccountCreateParams(
                username="Moderator_1",
                role=RoleEnum.MODERATOR,
                password=Secret("password123"),
                is_active=True,
            ),
            current_username="test",
        )

    def test_get_account(self) -> None:
        self.use_case.get_account.return_value = ManagedAccount(
            username="Admin",
            role=RoleEnum.ADMIN,
            is_active=True,
        )

        response = self.api.get_admin_account(username="ADMIN")

        self.asserts.status(response=response, expected_status=codes.OK)
        assert response.json() == {"username": "Admin", "role": "admin", "isActive": True}
        self.use_case.get_account.assert_called_once_with(username="ADMIN")

    def test_update_role(self) -> None:
        self.use_case.update_role.return_value = ManagedAccount(
            username="Moderator",
            role=RoleEnum.ADMIN,
            is_active=True,
        )

        response = self.api.put_admin_account_role(
            username="Moderator",
            data={"role": "admin"},
        )

        self.asserts.status(response=response, expected_status=codes.OK)
        assert response.json() == {"username": "Moderator", "role": "admin", "isActive": True}
        self.use_case.update_role.assert_called_once_with(
            username="Moderator",
            params=ManagedAccountRoleUpdateParams(role=RoleEnum.ADMIN),
            current_username="test",
        )

    def test_update_password(self) -> None:
        self.use_case.update_password.return_value = ManagedAccount(
            username="test",
            role=RoleEnum.ADMIN,
            is_active=True,
        )

        response = self.api.put_admin_account_password(
            username="test",
            data={"password": "password123"},
        )

        self.asserts.status(response=response, expected_status=codes.OK)
        assert response.json() == {"username": "test", "role": "admin", "isActive": True}
        self.use_case.update_password.assert_called_once_with(
            username="test",
            params=ManagedAccountPasswordUpdateParams(password=Secret("password123")),
            current_username="test",
        )

    def test_activate_account(self) -> None:
        self.use_case.activate_account.return_value = ManagedAccount(
            username="Moderator",
            role=RoleEnum.MODERATOR,
            is_active=True,
        )

        response = self.api.post_activate_admin_account(username="Moderator")

        self.asserts.status(response=response, expected_status=codes.OK)
        assert response.json() == {"username": "Moderator", "role": "moderator", "isActive": True}
        self.use_case.activate_account.assert_called_once_with(
            username="Moderator",
            current_username="test",
        )

    def test_deactivate_account(self) -> None:
        self.use_case.deactivate_account.return_value = ManagedAccount(
            username="Moderator",
            role=RoleEnum.MODERATOR,
            is_active=False,
        )

        response = self.api.post_deactivate_admin_account(username="Moderator")

        self.asserts.status(response=response, expected_status=codes.OK)
        assert response.json() == {
            "username": "Moderator",
            "role": "moderator",
            "isActive": False,
        }
        self.use_case.deactivate_account.assert_called_once_with(
            username="Moderator",
            current_username="test",
        )

    def test_delete_account(self) -> None:
        response = self.api.delete_admin_account(username="Moderator")

        self.asserts.status(response=response, expected_status=codes.NO_CONTENT)
        self.use_case.delete_account.assert_called_once_with(
            username="Moderator",
            current_username="test",
        )

    def test_create_account_validates_payload(self) -> None:
        response = self.api.post_create_admin_account(
            data={
                "username": "bad-name",
                "role": "user",
                "password": "short",
                "isActive": True,
            },
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_account.assert_not_called()

    def test_create_account_rejects_owner_role_at_api_boundary(self) -> None:
        response = self.api.post_create_admin_account(
            data={
                "username": "SecondOwner",
                "role": "owner",
                "password": "password123",
                "isActive": True,
            },
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_account.assert_not_called()

    def test_list_accounts_requires_pagination_query_params_at_api_boundary(self) -> None:
        response = self.api.get_admin_accounts(page=None, page_size=None)

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.list_accounts.assert_not_called()

    def test_role_update_rejects_regular_user_role(self) -> None:
        response = self.api.put_admin_account_role(
            username="Moderator",
            data={"role": "user"},
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.update_role.assert_not_called()

    def test_role_update_rejects_owner_role_at_api_boundary(self) -> None:
        response = self.api.put_admin_account_role(
            username="Admin",
            data={"role": "owner"},
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.update_role.assert_not_called()

    def test_requires_authentication(self) -> None:
        response = self.no_auth_api.get_admin_accounts()

        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)
        self.use_case.list_accounts.assert_not_called()

    def test_allows_owner_role(self) -> None:
        self.authentication_use_case.authenticate.return_value = JwtUser(
            username="owner",
            role=RoleEnum.OWNER,
        )
        self.use_case.list_accounts.return_value = self.factory.core.managed_accounts()

        response = self.api.get_admin_accounts()

        self.asserts.status(response=response, expected_status=codes.OK)

    def test_requires_team_manager_role(self) -> None:
        self.authentication_use_case.authenticate.return_value = JwtUser(
            username="moderator",
            role=RoleEnum.MODERATOR,
        )

        response = self.api.get_admin_accounts()

        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)
        self.use_case.list_accounts.assert_not_called()
