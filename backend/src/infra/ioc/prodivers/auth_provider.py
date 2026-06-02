from argon2 import PasswordHasher as CryptContext
from dishka import Provider, Scope, provide
from litestar import Request
from litestar.stores.valkey import ValkeyStore
from sqlalchemy.ext.asyncio import AsyncSession

from core.account.storages import UserAccountStorage
from core.auth.password_hashers import Argon2PasswordHasher, PasswordHasher
from core.auth.storages import AuthStorage, TokenRevocationStorage
from core.auth.token_handlers import PasetoTokenHandler, TokenHandler
from core.auth.types import RawToken, Token
from core.auth.use_cases import AbstractAuthUseCase, AuthUseCase
from infra.config.constants import constants
from infra.config.settings import settings
from infra.postgresql.storages.auth import AuthDatabaseStorage
from infra.valkey.storages import ValkeyTokenRevocationStorage


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def raw_token(self, request: Request) -> RawToken:
        return RawToken(request.headers.get(settings.auth.token_header_name, ""))

    @provide(scope=Scope.REQUEST)
    async def token(self, raw_token: RawToken) -> Token:
        return Token(raw_token.split(settings.auth.token_prefix)[-1].strip().encode())

    @provide(scope=Scope.APP)
    async def provide_hasher(self) -> PasswordHasher:
        return Argon2PasswordHasher(context=CryptContext())

    @provide(scope=Scope.APP)
    async def provide_token_handler(self) -> TokenHandler:
        return PasetoTokenHandler(
            public_key_pem=settings.auth.public_key.to_domain_secret(),
            secret_key_pem=settings.auth.private_key.to_domain_secret(),
            token_expire_seconds=settings.auth.token_expire_seconds,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_auth_storage(self, session: AsyncSession) -> AuthStorage:
        return AuthDatabaseStorage(session=session)

    @provide(scope=Scope.APP)
    async def provide_token_revocation_storage(self) -> TokenRevocationStorage:
        return ValkeyTokenRevocationStorage(
            store=ValkeyStore.with_client(
                url=settings.valkey.get_url(
                    db=constants.valkey.databases.auth_revocations,
                ).get_secret_value(),
                db=constants.valkey.databases.auth_revocations,
                port=settings.valkey.port,
                namespace=constants.valkey.namespaces.auth_revocations,
            ),
        )

    @provide(scope=Scope.REQUEST)
    async def provide_auth_use_case(
        self,
        hasher: PasswordHasher,
        token_handler: TokenHandler,
        auth_storage: AuthStorage,
        token_revocation_storage: TokenRevocationStorage,
        user_storage: UserAccountStorage,
    ) -> AbstractAuthUseCase:
        return AuthUseCase(
            hasher=hasher,
            token_handler=token_handler,
            auth_storage=auth_storage,
            token_revocation_storage=token_revocation_storage,
            user_storage=user_storage,
        )
