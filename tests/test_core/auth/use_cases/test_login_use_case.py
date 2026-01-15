import pytest
import pytest_asyncio

from core.auth.enums import RoleEnum
from core.auth.exceptions import UserNotFoundError, UnauthorizedError, ForbiddenError
from core.auth.schemas import JwtUser
from core.auth.use_cases import LoginUseCase
from tests.fixtures import FactoryFixture, ContainerFixture


class TestLoginUseCase(ContainerFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.hasher = await self.container.get_hasher()
        self.token_handler = await self.container.get_token_handler()
        self.storage = await self.container.get_auth_storage()
        self.use_case = LoginUseCase(
            hasher=self.hasher,
            token_handler=self.token_handler,
            storage=self.storage,
        )

    async def test_login_user_not_found(self) -> None:
        self.storage.get_user_by_username.side_effect = UserNotFoundError
        with pytest.raises(UnauthorizedError):
            await self.use_case.execute(
                username="test",
                password="test",
                required_role=RoleEnum.ADMIN,
            )

    async def test_login_user_role_not_has_role(self) -> None:
        self.storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.USER,
        )
        with pytest.raises(ForbiddenError):
            await self.use_case.execute(
                username="test",
                password="test",
                required_role=RoleEnum.ADMIN,
            )

    async def test_login_not_verified_password(self) -> None:
        self.hasher.verify_password.return_value = (False, False)
        self.storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
        )
        with pytest.raises(UnauthorizedError):
            await self.use_case.execute(
                username="test",
                password="test",
                required_role=RoleEnum.ADMIN,
            )

    async def test_login_rehash_on_password_expire(self) -> None:
        self.token_handler.encode_token.return_value = "TOKEN".encode()
        self.hasher.verify_password.return_value = (True, True)
        self.hasher.hash_password.return_value = "new_password"
        self.storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
        )
        token = await self.use_case.execute(
            username="test",
            password="test",
            required_role=RoleEnum.ADMIN,
        )
        assert token == self.factory.core.token("TOKEN".encode())
        self.storage.update_user_password_hash.assert_called_once_with(
            username="test",
            password_hash="new_password",
        )

    async def test_login(self) -> None:
        self.token_handler.encode_token.return_value = "TOKEN".encode()
        self.hasher.verify_password.return_value = (True, False)
        self.storage.get_user_by_username.return_value = self.factory.core.user(
            username="test",
            password_hash="test",
            role=RoleEnum.ADMIN,
        )
        token = await self.use_case.execute(
            username="test",
            password="test",
            required_role=RoleEnum.ADMIN,
        )
        assert token == self.factory.core.token("TOKEN".encode())
        self.storage.get_user_by_username.assert_called_once_with(username="test")
        self.hasher.verify_password.assert_called_once_with(
            plain_password="test",
            hashed_password="test",
        )
        self.token_handler.encode_token.assert_called_once_with(
            payload=JwtUser(username="test", role=RoleEnum.ADMIN),
        )
