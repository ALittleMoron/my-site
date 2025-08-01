from unittest.mock import Mock

from dishka import Provider, BaseScope, Component, provide, Scope
from passlib.context import CryptContext

from config.settings import Settings
from core.schemas import Secret
from db.storages.auth import AuthStorage
from entrypoints.admin.auth.handlers import AuthHandler
from entrypoints.admin.auth.utils import Hasher

test_public_key_pem = """\
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAgiimqA4yuUL9ahhsRGooZXoO4XTDzmK+pu4mJnfdPIk=
-----END PUBLIC KEY-----
"""
test_private_key_pem = """\
-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIHvAarrKpuBdN5qcsk7uVGwHA3HuzMr0j7ZGvIruVb+B
-----END PRIVATE KEY-----
"""


class MockAuthProvider(Provider):
    def __init__(
        self,
        settings: Settings,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ) -> None:
        super().__init__(scope=scope, component=component)
        self.settings = settings

    @provide(scope=Scope.APP)
    async def provide_hasher(self) -> Hasher:
        return Hasher(context=CryptContext(schemes=self.settings.auth.crypto_scheme))

    @provide(scope=Scope.APP)
    async def provide_auth_handler(self) -> AuthHandler:
        return AuthHandler(
            public_key_pem=test_public_key_pem,
            secret_key_pem=Secret(test_private_key_pem),
            token_expire_seconds=self.settings.auth.token_expire_seconds,
        )

    @provide(scope=Scope.APP)
    async def provide_auth_storage(self) -> AuthStorage:
        mock = Mock(spec=AuthStorage)
        return mock
