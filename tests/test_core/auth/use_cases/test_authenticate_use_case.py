import pytest
import pytest_asyncio

from core.auth.enums import RoleEnum
from core.auth.exceptions import UnauthorizedError, UserNotFoundError
from core.auth.use_cases import AuthenticateUseCase
from tests.fixtures import FactoryFixture, ContainerFixture


class TestLoginUseCase(ContainerFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.token_handler = await self.container.get_token_handler()
        self.storage = await self.container.get_auth_storage()
        self.use_case = AuthenticateUseCase(
            token_handler=self.token_handler,
            user_storage=self.storage,
        )

    async def test_authenticate_token_decode_error(self) -> None:
        self.token_handler.decode_token.side_effect = UnauthorizedError
        token = await self.use_case.execute(token="invalid_token", required_role=RoleEnum.ADMIN)
        assert token is None
        self.token_handler.decode_token.assert_called_once_with("invalid_token".encode())

    async def test_authenticate_user_not_found(self) -> None:
        self.storage.get_user_by_username.side_effect = UserNotFoundError
        self.token_handler.decode_token.return_value = self.factory.core.jwt_user(
            username="test",
            role=RoleEnum.ADMIN,
        )
        token = await self.use_case.execute(token="valid_token", required_role=RoleEnum.ADMIN)
        assert token is None
        self.storage.get_user_by_username.assert_called_once_with(username="test")

    @pytest.mark.parametrize(
        ["required_role", "user_role"],
        [
            (RoleEnum.ADMIN, RoleEnum.USER),
            (RoleEnum.USER, RoleEnum.ADMIN),
        ],
    )
    async def test_authenticate_user_not_has_role(
        self,
        required_role: RoleEnum,
        user_role: RoleEnum,
    ) -> None:
        self.storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=user_role,
        )
        self.token_handler.decode_token.return_value = self.factory.core.jwt_user(
            username="test",
            role=user_role,
        )
        token = await self.use_case.execute(token="valid_token", required_role=required_role)
        assert token is None

    async def test_authenticate(self) -> None:
        self.storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
        )
        self.token_handler.decode_token.return_value = self.factory.core.jwt_user(
            username="test",
            role=RoleEnum.ADMIN,
        )
        self.token_handler.encode_token.return_value = "NEW_TOKEN".encode()
        token = await self.use_case.execute(token="valid_token", required_role=RoleEnum.ADMIN)
        assert token == "NEW_TOKEN".encode()
