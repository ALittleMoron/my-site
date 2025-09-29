from argon2 import PasswordHasher as CryptContext
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from core.auth.password_hashers import Argon2PasswordHasher, PasswordHasher
from core.auth.storages import AuthStorage
from core.auth.token_handlers import PasetoTokenHandler, TokenHandler
from core.auth.use_cases import (
    AbstractAuthenticateUseCase,
    AbstractLoginUseCase,
    AuthenticateUseCase,
    LoginUseCase,
)
from db.storages.auth import AuthDatabaseStorage


class AuthProvider(Provider):
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

    @provide(scope=Scope.REQUEST)
    async def provide_login_use_case(
        self,
        hasher: PasswordHasher,
        token_handler: TokenHandler,
        storage: AuthStorage,
    ) -> AbstractLoginUseCase:
        return LoginUseCase(hasher=hasher, token_handler=token_handler, storage=storage)

    @provide(scope=Scope.REQUEST)
    async def provide_authenticate_use_case(
        self,
        token_handler: TokenHandler,
        storage: AuthStorage,
    ) -> AbstractAuthenticateUseCase:
        return AuthenticateUseCase(token_handler=token_handler, storage=storage)
