from dishka import Provider, Scope, provide
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from core.auth.password_hashers import PasslibPasswordHasher, PasswordHasher
from core.auth.token_handlers import PasetoTokenHandler, TokenHandler
from db.storages.auth import AuthDatabaseStorage, AuthStorage


class AuthProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_hasher(self) -> PasswordHasher:
        return PasslibPasswordHasher(context=CryptContext(schemes=settings.auth.crypto_scheme))

    @provide(scope=Scope.APP)
    async def provide_auth_handler(self) -> TokenHandler:
        return PasetoTokenHandler(
            public_key_pem=settings.auth.public_key.to_domain_secret(),
            secret_key_pem=settings.auth.private_key.to_domain_secret(),
            token_expire_seconds=settings.auth.token_expire_seconds,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_auth_storage(self, session: AsyncSession) -> AuthStorage:
        return AuthDatabaseStorage(session=session)
