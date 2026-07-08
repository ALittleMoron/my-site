from dataclasses import dataclass
from datetime import datetime
from typing import cast

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.exceptions import AuthSessionNotFoundError, UserNotFoundError
from core.auth.schemas import AuthSession, AuthSessionCreate
from core.auth.storages import AuthSessionStorage, AuthStorage
from core.auth.types import SessionSecretHash
from infra.postgresql.models import AuthSessionModel, UserModel


@dataclass(kw_only=True)
class AuthDatabaseStorage(AuthStorage):
    session: AsyncSession

    async def update_user_password_hash(self, username: str, password_hash: str) -> None:
        stmt = (
            update(UserModel)
            .values(password_hash=password_hash)
            .where(func.lower(UserModel.username) == username.lower())
            .returning(UserModel.username)
        )
        db_username = await self.session.scalar(stmt)
        if db_username is None:
            raise UserNotFoundError


@dataclass(kw_only=True)
class AuthSessionDatabaseStorage(AuthSessionStorage):
    session: AsyncSession

    async def create_session(self, *, session: AuthSessionCreate) -> AuthSession:
        statement = (
            insert(AuthSessionModel)
            .values(
                username=session.username,
                secret_hash=session.secret_hash,
                expires_at=session.expires_at,
                is_revoked=session.is_revoked,
            )
            .returning(AuthSessionModel)
        )
        model = await self.session.scalar(statement)
        if model is None:
            raise AuthSessionNotFoundError
        return model.to_domain_schema()

    async def get_session_by_secret_hash(self, *, secret_hash: SessionSecretHash) -> AuthSession:
        statement = select(AuthSessionModel).where(AuthSessionModel.secret_hash == secret_hash)
        model = await self.session.scalar(statement)
        if model is None:
            raise AuthSessionNotFoundError
        return model.to_domain_schema()

    async def get_session_by_id(self, *, session_id: str) -> AuthSession:
        statement = select(AuthSessionModel).where(AuthSessionModel.id == session_id)
        model = await self.session.scalar(statement)
        if model is None:
            raise AuthSessionNotFoundError
        return model.to_domain_schema()

    async def extend_session_expiry(self, *, session_id: str, expires_at: datetime) -> None:
        statement = (
            update(AuthSessionModel)
            .values(expires_at=expires_at)
            .where(AuthSessionModel.id == session_id)
            .returning(AuthSessionModel.id)
        )
        stored_session_id = await self.session.scalar(statement)
        if stored_session_id is None:
            raise AuthSessionNotFoundError

    async def delete_expired_sessions(self, *, expires_at: datetime) -> int:
        statement = delete(AuthSessionModel).where(AuthSessionModel.expires_at <= expires_at)
        result = await self.session.execute(statement)
        rowcount = cast("int | None", getattr(result, "rowcount", None))
        if rowcount is None:
            return 0
        return rowcount

    async def revoke_session_by_secret_hash(self, *, secret_hash: SessionSecretHash) -> None:
        statement = (
            update(AuthSessionModel)
            .values(is_revoked=True)
            .where(AuthSessionModel.secret_hash == secret_hash)
            .returning(AuthSessionModel.id)
        )
        session_id = await self.session.scalar(statement)
        if session_id is None:
            raise AuthSessionNotFoundError

    async def revoke_user_sessions(self, *, username: str) -> None:
        statement = (
            update(AuthSessionModel)
            .values(is_revoked=True)
            .where(func.lower(AuthSessionModel.username) == username.lower())
        )
        await self.session.execute(statement)
