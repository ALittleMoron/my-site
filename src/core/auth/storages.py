from abc import ABC, abstractmethod

from core.auth.schemas import User


class AuthStorage(ABC):
    @abstractmethod
    async def get_user_by_username(self, username: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update_user_password_hash(self, username: str, password_hash: str) -> None:
        raise NotImplementedError
