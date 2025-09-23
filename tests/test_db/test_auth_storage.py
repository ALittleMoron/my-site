import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.enums import RoleEnum
from core.auth.exceptions import UserNotFoundError
from db.storages.auth import AuthDatabaseStorage
from tests.fixtures import FactoryFixture, StorageFixture


class TestAuthStorage(FactoryFixture, StorageFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, session: AsyncSession) -> None:
        self.storage = AuthDatabaseStorage(session=session)
        await self.storage_helper.create_users(
            users=[
                self.factory.core.user(
                    username="user1",
                    password_hash="password1",
                    role=RoleEnum.USER,
                ),
                self.factory.core.user(
                    username="user2",
                    password_hash="password2",
                    role=RoleEnum.ADMIN,
                ),
            ]
        )

    async def test_get_user_by_username_not_found(self) -> None:
        with pytest.raises(UserNotFoundError):
            await self.storage.get_user_by_username(username="NOT_FOUND")

    async def test_get_user_by_username(self) -> None:
        user = await self.storage.get_user_by_username(username="user1")
        assert user == self.factory.core.user(
            username="user1",
            password_hash="password1",
            role=RoleEnum.USER,
        )

    async def test_update_user_password_not_found(self) -> None:
        with pytest.raises(UserNotFoundError):
            await self.storage.update_user_password_hash(
                username="user3",
                password_hash="NEW_PASSWORD",
            )

    async def test_update_user_password(self) -> None:
        await self.storage.update_user_password_hash(username="user1", password_hash="NEW_PASSWORD")
        user = await self.storage.get_user_by_username(username="user1")
        assert user == self.factory.core.user(
            username="user1",
            password_hash="NEW_PASSWORD",
            role=RoleEnum.USER,
        )
