from dishka import Provider, Scope, provide
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from config.constants import constants
from config.settings import settings
from core.schemas import Secret
from db.storages.auth import AuthDatabaseStorage, AuthStorage
from entrypoints.admin.auth.handlers import AuthHandler
from entrypoints.admin.auth.utils import Hasher


class AuthProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_hasher(self) -> Hasher:
        return Hasher(context=CryptContext(schemes=settings.auth.crypto_scheme))

    @provide(scope=Scope.APP)
    async def provide_auth_handler(self) -> AuthHandler:
        return AuthHandler(
            public_key_pem=(constants.dir.certs_path / "public.pem").read_text(),
            secret_key_pem=Secret((constants.dir.certs_path / "private.pem").read_text()),
            token_expire_seconds=settings.auth.token_expire_seconds,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_auth_storage(self, session: AsyncSession) -> AuthStorage:
        return AuthDatabaseStorage(session=session)
