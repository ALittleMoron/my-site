from abc import ABC, abstractmethod

from core.auth.schemas import User


class GetUserByUsernameAuthStorage(ABC):
    @abstractmethod
    async def get_user_by_username(self, username: str) -> User:
        raise NotImplementedError


class UpdateUserPasswordHashAuthStorage(ABC):
    @abstractmethod
    async def update_user_password_hash(self, username: str, password_hash: str) -> None:
        raise NotImplementedError


class UserAuthStorage(GetUserByUsernameAuthStorage, UpdateUserPasswordHashAuthStorage, ABC):
    pass


class AuthStorage(UserAuthStorage, ABC):
    pass
