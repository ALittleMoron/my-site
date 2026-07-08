# ruff: noqa: S106
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.enums import RoleEnum
from core.auth.exceptions import AuthSessionNotFoundError, UserNotFoundError
from core.auth.schemas import AuthSession, AuthSessionCreate
from core.auth.types import SessionSecretHash
from infra.postgresql.storages.auth import AuthDatabaseStorage, AuthSessionDatabaseStorage
from infra.postgresql.storages.users import UserAccountDatabaseStorage
from tests.test_cases import StorageTestCase


class TestAuthStorage(StorageTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, session: AsyncSession) -> None:
        self.user_storage = UserAccountDatabaseStorage(session=session)
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
            ],
        )

    async def test_update_user_password_not_found(self) -> None:
        with pytest.raises(UserNotFoundError):
            await self.storage.update_user_password_hash(
                username="user3",
                password_hash="NEW_PASSWORD",
            )

    async def test_update_user_password(self) -> None:
        await self.storage.update_user_password_hash(username="user1", password_hash="NEW_PASSWORD")
        user = await self.user_storage.get_user_by_username(username="user1")
        assert user == self.factory.core.user(
            username="user1",
            password_hash="NEW_PASSWORD",
            role=RoleEnum.USER,
        )


class TestAuthSessionStorage(StorageTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, session: AsyncSession) -> None:
        self.storage = AuthSessionDatabaseStorage(session=session)
        self.now = datetime(2026, 7, 8, 11, 30, tzinfo=UTC)
        await self.storage_helper.create_users(
            users=[
                self.factory.core.user(
                    username="admin",
                    password_hash="password1",
                    role=RoleEnum.ADMIN,
                ),
                self.factory.core.user(
                    username="moderator",
                    password_hash="password2",
                    role=RoleEnum.MODERATOR,
                ),
            ],
        )

    async def test_get_session_by_secret_hash_not_found(self) -> None:
        with pytest.raises(AuthSessionNotFoundError):
            await self.storage.get_session_by_secret_hash(
                secret_hash=SessionSecretHash("missing"),
            )

    async def test_create_and_get_session(self) -> None:
        session = AuthSessionCreate(
            username="admin",
            secret_hash=SessionSecretHash(
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            ),
            expires_at=self.now + timedelta(days=30),
            is_revoked=False,
        )

        created = await self.storage.create_session(session=session)
        stored = await self.storage.get_session_by_secret_hash(
            secret_hash=session.secret_hash,
        )
        expected = AuthSession(
            id=created.id,
            username=session.username,
            secret_hash=session.secret_hash,
            expires_at=session.expires_at,
            is_revoked=session.is_revoked,
        )

        assert len(created.id) == 32
        assert created == expected
        assert stored == expected
        assert await self.storage.get_session_by_id(session_id=created.id) == expected

    async def test_revoke_session_by_secret_hash(self) -> None:
        session = AuthSessionCreate(
            username="admin",
            secret_hash=SessionSecretHash(
                "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            ),
            expires_at=self.now + timedelta(days=30),
            is_revoked=False,
        )
        created = await self.storage.create_session(session=session)

        await self.storage.revoke_session_by_secret_hash(secret_hash=session.secret_hash)

        stored = await self.storage.get_session_by_id(session_id=created.id)
        assert stored == AuthSession(
            id=created.id,
            username=session.username,
            secret_hash=session.secret_hash,
            expires_at=session.expires_at,
            is_revoked=True,
        )

    async def test_revoke_user_sessions_case_insensitively(self) -> None:
        admin_session = AuthSessionCreate(
            username="admin",
            secret_hash=SessionSecretHash(
                "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
            ),
            expires_at=self.now + timedelta(days=30),
            is_revoked=False,
        )
        moderator_session = AuthSessionCreate(
            username="moderator",
            secret_hash=SessionSecretHash(
                "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
            ),
            expires_at=self.now + timedelta(days=30),
            is_revoked=False,
        )
        created_admin_session = await self.storage.create_session(session=admin_session)
        created_moderator_session = await self.storage.create_session(session=moderator_session)

        await self.storage.revoke_user_sessions(username="ADMIN")

        assert (
            await self.storage.get_session_by_id(session_id=created_admin_session.id)
        ).is_revoked
        assert not (
            await self.storage.get_session_by_id(session_id=created_moderator_session.id)
        ).is_revoked
