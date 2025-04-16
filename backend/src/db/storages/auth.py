from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.exceptions import UserNotFoundError
from core.auth.schemas import User
from db.models import UserModel


class AuthStorage(ABC):
    @abstractmethod
    async def get_user_by_username(self, username: str) -> User:
        raise NotImplementedError


@dataclass(kw_only=True)
class AuthDatabaseStorage(AuthStorage):
    session: AsyncSession

    async def get_user_by_username(self, username: str) -> User:
        stmt = select(UserModel).where(UserModel.username == username)
        user = await self.session.scalar(stmt)
        if user is None:
            raise UserNotFoundError
        return user.to_domain_schema()
