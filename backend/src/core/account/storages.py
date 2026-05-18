from abc import ABC, abstractmethod

from core.auth.schemas import User


class GetUserByUsernameStorage(ABC):
    @abstractmethod
    async def get_user_by_username(self, username: str) -> User:
        raise NotImplementedError


class UserAccountStorage(GetUserByUsernameStorage, ABC):
    pass
