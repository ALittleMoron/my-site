from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.account.storages import UserAccountStorage
from core.auth.enums import RoleEnum
from core.auth.exceptions import ForbiddenError, UnauthorizedError, UserNotFoundError
from core.auth.password_hashers import PasswordHasher
from core.auth.schemas import JwtUser, User
from core.auth.storages import AuthStorage, TokenRevocationStorage
from core.auth.token_handlers import TokenHandler
from core.auth.types import Token
from infra.config.loggers import logger


class AbstractAuthUseCase(ABC):
    @abstractmethod
    async def login(self, username: str, password: str, required_role: RoleEnum) -> Token:
        raise NotImplementedError

    @abstractmethod
    async def authenticate(self, token: Token, required_role: RoleEnum) -> User:
        raise NotImplementedError

    @abstractmethod
    async def logout(self, token: Token) -> None:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class AuthUseCase(AbstractAuthUseCase):
    hasher: PasswordHasher
    token_handler: TokenHandler
    auth_storage: AuthStorage
    token_revocation_storage: TokenRevocationStorage
    user_storage: UserAccountStorage

    async def login(self, username: str, password: str, required_role: RoleEnum) -> Token:
        try:
            user = await self.user_storage.get_user_by_username(username=username)
        except UserNotFoundError as exc:
            logger.warning(event="No user in db from username form field", username=username)
            raise UnauthorizedError from exc
        if not user.has_role(role=required_role):
            logger.warning(f"User has no role {required_role.value}", username=user.username)
            raise ForbiddenError
        verified, need_rehash = self.hasher.verify_password(
            plain_password=password,
            hashed_password=user.password_hash.get_secret_value(),
        )
        if not verified:
            logger.warning(
                "incorrect credentials (passwords not suit)",
                username=user.username,
            )
            raise UnauthorizedError
        if need_rehash:
            await self.auth_storage.update_user_password_hash(
                username=username,
                password_hash=self.hasher.hash_password(password),
            )
        return Token(self.token_handler.encode_token(payload=JwtUser.from_user(user=user)))

    async def authenticate(self, token: Token, required_role: RoleEnum) -> User:
        if await self.token_revocation_storage.is_token_revoked(token=token):
            logger.warning(event="Revoked token used for authentication")
            raise UnauthorizedError
        payload = self.token_handler.decode_token(token)
        try:
            user = await self.user_storage.get_user_by_username(username=payload.username)
        except UserNotFoundError as exc:
            logger.warning(event="No user in db from token payload", payload=payload)
            raise UnauthorizedError from exc
        if not user.has_role(role=required_role):
            logger.warning(f"User has no role {required_role.value}", username=user.username)
            raise ForbiddenError
        return user

    async def logout(self, token: Token) -> None:
        try:
            remaining_seconds = self.token_handler.get_token_remaining_seconds(token)
        except UnauthorizedError:
            logger.warning(event="Logout requested with invalid token")
            return
        if remaining_seconds is None:
            logger.warning(event="Logout requested with token that cannot be revoked")
            return
        await self.token_revocation_storage.revoke_token(
            token=token,
            expires_in_seconds=remaining_seconds,
        )
