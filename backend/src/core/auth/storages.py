from abc import ABC, abstractmethod

from core.auth.types import Token


class TokenRevocationStorage(ABC):
    @abstractmethod
    async def revoke_token(self, token: Token, expires_in_seconds: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def is_token_revoked(self, token: Token) -> bool:
        raise NotImplementedError


class AuthStorage(ABC):
    @abstractmethod
    async def update_user_password_hash(self, username: str, password_hash: str) -> None:
        raise NotImplementedError
