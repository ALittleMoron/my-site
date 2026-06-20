from dataclasses import dataclass

from core.account.storages import UserAccountStorage
from core.auth.enums import RoleEnum
from core.auth.event_dispatchers import AuthEventReporter
from core.auth.exceptions import ForbiddenError, UnauthorizedError, UserNotFoundError
from core.auth.password_hashers import PasswordHasher
from core.auth.schemas import JwtUser, User
from core.auth.storages import AuthStorage, TokenRevocationStorage
from core.auth.token_handlers import TokenHandler
from core.auth.types import Token


@dataclass(kw_only=True, slots=True, frozen=True)
class AuthUseCase:
    hasher: PasswordHasher
    token_handler: TokenHandler
    auth_storage: AuthStorage
    token_revocation_storage: TokenRevocationStorage
    user_storage: UserAccountStorage
    event_reporter: AuthEventReporter

    async def login(self, username: str, password: str, required_role: RoleEnum) -> Token:
        try:
            user = await self.user_storage.get_user_by_username(username=username)
        except UserNotFoundError as exc:
            self.event_reporter.report_login_user_not_found(username=username)
            raise UnauthorizedError from exc
        if not user.has_role(role=required_role):
            self.event_reporter.report_login_role_forbidden(
                username=user.username,
                required_role=required_role,
            )
            raise ForbiddenError
        verified, need_rehash = self.hasher.verify_password(
            plain_password=password,
            hashed_password=user.password_hash.get_secret_value(),
        )
        if not verified:
            self.event_reporter.report_login_password_verification_failed(username=user.username)
            raise UnauthorizedError
        if need_rehash:
            await self.auth_storage.update_user_password_hash(
                username=username,
                password_hash=self.hasher.hash_password(password),
            )
        return Token(self.token_handler.encode_token(payload=JwtUser.from_user(user=user)))

    async def authenticate(self, token: Token, required_role: RoleEnum) -> User:
        if await self.token_revocation_storage.is_token_revoked(token=token):
            self.event_reporter.report_authentication_revoked_token_used()
            raise UnauthorizedError
        payload = self.token_handler.decode_token(token)
        try:
            user = await self.user_storage.get_user_by_username(username=payload.username)
        except UserNotFoundError as exc:
            self.event_reporter.report_authentication_user_not_found(username=payload.username)
            raise UnauthorizedError from exc
        if not user.has_role(role=required_role):
            self.event_reporter.report_authentication_role_forbidden(
                username=user.username,
                required_role=required_role,
            )
            raise ForbiddenError
        return user

    async def logout(self, token: Token) -> None:
        try:
            remaining_seconds = self.token_handler.get_token_remaining_seconds(token)
        except UnauthorizedError:
            self.event_reporter.report_logout_invalid_token()
            return
        if remaining_seconds is None:
            self.event_reporter.report_logout_token_without_remaining_lifetime()
            return
        await self.token_revocation_storage.revoke_token(
            token=token,
            expires_in_seconds=remaining_seconds,
        )
