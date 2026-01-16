from dataclasses import dataclass

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.exceptions import UserNotFoundError
from core.auth.storages import AuthStorage
from db.models import UserModel


@dataclass(kw_only=True)
class AuthDatabaseStorage(AuthStorage):
    session: AsyncSession

    async def update_user_password_hash(self, username: str, password_hash: str) -> None:
        stmt = (
            update(UserModel)
            .values(password_hash=password_hash)
            .where(UserModel.username == username)
            .returning(UserModel.username)
        )
        db_username = await self.session.scalar(stmt)
        if db_username is None:
            raise UserNotFoundError
