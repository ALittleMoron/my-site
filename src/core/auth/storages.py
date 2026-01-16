from abc import ABC, abstractmethod


class UpdateUserPasswordHashStorage(ABC):
    @abstractmethod
    async def update_user_password_hash(self, username: str, password_hash: str) -> None:
        raise NotImplementedError


class AuthStorage(UpdateUserPasswordHashStorage, ABC):
    pass
