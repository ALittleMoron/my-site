import pytest
import pytest_asyncio

from core.auth.enums import RoleEnum
from core.auth.exceptions import UnauthorizedError, UserNotFoundError, ForbiddenError
from core.auth.types import Token
from core.auth.use_cases import AuthenticateUseCase
from tests.fixtures import FactoryFixture, ContainerFixture


class TestLoginUseCase(ContainerFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.token_handler = await self.container.get_token_handler()
        self.user_storage = await self.container.get_user_storage()
        self.use_case = AuthenticateUseCase(
            token_handler=self.token_handler,
            user_storage=self.user_storage,
        )

    async def test_authenticate_token_decode_error(self) -> None:
        self.token_handler.decode_token.side_effect = UnauthorizedError
        with pytest.raises(UnauthorizedError):
            await self.use_case.execute(
                token=Token("invalid_token".encode()),
                required_role=RoleEnum.ADMIN,
            )
        self.token_handler.decode_token.assert_called_once_with("invalid_token".encode())

    async def test_authenticate_user_not_found(self) -> None:
        self.user_storage.get_user_by_username.side_effect = UserNotFoundError
        self.token_handler.decode_token.return_value = self.factory.core.jwt_user(
            username="test",
            role=RoleEnum.ADMIN,
        )
        with pytest.raises(UnauthorizedError):
            await self.use_case.execute(
                token=Token("valid_token".encode()),
                required_role=RoleEnum.ADMIN,
            )
        self.user_storage.get_user_by_username.assert_called_once_with(username="test")

    async def test_authenticate_user_not_has_role(self) -> None:
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.USER,
        )
        self.token_handler.decode_token.return_value = self.factory.core.jwt_user(
            username="test",
            role=RoleEnum.USER,
        )
        with pytest.raises(ForbiddenError):
            await self.use_case.execute(
                token=Token("valid_token".encode()),
                required_role=RoleEnum.ADMIN,
            )

    async def test_authenticate(self) -> None:
        self.user_storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
        )
        self.token_handler.decode_token.return_value = self.factory.core.jwt_user(
            username="test",
            role=RoleEnum.ADMIN,
        )
        self.token_handler.encode_token.return_value = "NEW_TOKEN".encode()
        user = await self.use_case.execute(
            token=Token("valid_token".encode()),
            required_role=RoleEnum.ADMIN,
        )
        assert user == self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
        )
