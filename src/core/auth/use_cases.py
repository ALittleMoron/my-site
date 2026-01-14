from abc import ABC, abstractmethod
from dataclasses import dataclass

from config.loggers import logger
from core.auth.enums import RoleEnum
from core.auth.exceptions import UnauthorizedError, UserNotFoundError
from core.auth.password_hashers import PasswordHasher
from core.auth.schemas import JwtUser
from core.auth.storages import AuthStorage, UserAuthStorage
from core.auth.token_handlers import TokenHandler
from core.use_cases import UseCase


class AbstractLoginUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self, username: str, password: str, required_role: RoleEnum) -> bytes | None:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class LoginUseCase(AbstractLoginUseCase):
    hasher: PasswordHasher
    token_handler: TokenHandler
    storage: AuthStorage

    async def execute(self, username: str, password: str, required_role: RoleEnum) -> bytes | None:
        try:
            user = await self.storage.get_user_by_username(username=username)
        except UserNotFoundError:
            logger.warning(event="No user in db from username form field", username=username)
            return None
        if not user.has_role(role=required_role):
            logger.warning(f"User has no role {required_role.value}", username=user.username)
            return None
        verified, need_rehash = self.hasher.verify_password(
            plain_password=password,
            hashed_password=user.password_hash.get_secret_value(),
        )
        if not verified:
            logger.warning(
                "incorrect credentials (passwords not suit)",
                username=user.username,
            )
            return None
        if need_rehash:
            await self.storage.update_user_password_hash(
                username=username,
                password_hash=self.hasher.hash_password(password),
            )
        return self.token_handler.encode_token(payload=JwtUser.from_user(user=user))


class AbstractAuthenticateUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self, token: str, required_role: RoleEnum) -> bytes | None:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class AuthenticateUseCase(AbstractAuthenticateUseCase):
    token_handler: TokenHandler
    user_storage: UserAuthStorage

    async def execute(self, token: str, required_role: RoleEnum) -> bytes | None:
        try:
            payload = self.token_handler.decode_token(token.encode())
        except UnauthorizedError:
            return None
        try:
            user = await self.user_storage.get_user_by_username(username=payload.username)
        except UserNotFoundError:
            logger.warning(event="No user in db from token payload", payload=payload)
            return None
        if not user.has_role(role=required_role):
            logger.warning(f"User has no role {required_role.value}", username=user.username)
            return None
        return self.token_handler.encode_token(payload=JwtUser.from_user(user=user))
