from abc import ABC, abstractmethod
from dataclasses import dataclass

from config.loggers import logger
from core.auth.enums import RoleEnum
from core.auth.exceptions import ForbiddenError, UnauthorizedError, UserNotFoundError
from core.auth.password_hashers import PasswordHasher
from core.auth.schemas import JwtUser, User
from core.auth.storages import AuthStorage, UserAuthStorage
from core.auth.token_handlers import TokenHandler
from core.auth.types import Token
from core.use_cases import UseCase


class AbstractLoginUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self, username: str, password: str, required_role: RoleEnum) -> Token:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class LoginUseCase(AbstractLoginUseCase):
    hasher: PasswordHasher
    token_handler: TokenHandler
    storage: AuthStorage

    async def execute(self, username: str, password: str, required_role: RoleEnum) -> Token:
        try:
            user = await self.storage.get_user_by_username(username=username)
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
            await self.storage.update_user_password_hash(
                username=username,
                password_hash=self.hasher.hash_password(password),
            )
        return Token(self.token_handler.encode_token(payload=JwtUser.from_user(user=user)))


class AbstractAuthenticateUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self, token: Token, required_role: RoleEnum) -> User:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class AuthenticateUseCase(AbstractAuthenticateUseCase):
    token_handler: TokenHandler
    user_storage: UserAuthStorage

    async def execute(self, token: Token, required_role: RoleEnum) -> User:
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


class AbstractLogoutUseCase(UseCase, ABC):
    @abstractmethod
    async def execute(self, token: Token) -> None:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class LogoutUseCase(AbstractLogoutUseCase):
    async def execute(self, token: Token) -> None:
        pass
