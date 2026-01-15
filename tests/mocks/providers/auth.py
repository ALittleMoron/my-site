from unittest.mock import Mock

from dishka import Provider, BaseScope, Component, provide, Scope

from config.settings import Settings
from core.auth.password_hashers import PasswordHasher
from core.auth.schemas import JwtUser
from core.auth.storages import AuthStorage
from core.auth.token_handlers import TokenHandler
from core.auth.types import Token, RawToken
from core.auth.use_cases import (
    AbstractLoginUseCase,
    AbstractAuthenticateUseCase,
    AbstractLogoutUseCase,
)

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
        raw_token: RawToken,
        user: JwtUser,
        settings: Settings,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ) -> None:
        super().__init__(scope=scope, component=component)
        self.settings = settings
        self.user = user
        self.raw_token = raw_token

    @provide(scope=Scope.APP)
    async def provide_raw_token(self) -> RawToken:
        return self.raw_token

    @provide(scope=Scope.APP)
    async def provide_token(self, raw_token: RawToken) -> Token:
        return Token(raw_token.split(self.settings.auth.token_prefix)[-1].strip().encode())

    @provide(scope=Scope.APP)
    async def provide_hasher(self) -> PasswordHasher:
        mock = Mock(spec=PasswordHasher)
        mock.verify_password.return_value = True, False
        mock.hash_password.return_value = "1234"
        return mock

    @provide(scope=Scope.APP)
    async def provide_token_handler(self) -> TokenHandler:
        mock = Mock(spec=TokenHandler)
        mock.encode_token.return_value = "TOKEN".encode()
        mock.decode_token.return_value = self.user
        return mock

    @provide(scope=Scope.APP)
    async def provide_auth_storage(self) -> AuthStorage:
        mock = Mock(spec=AuthStorage)
        return mock

    @provide(scope=Scope.APP)
    async def provide_login_use_case(self) -> AbstractLoginUseCase:
        mock = Mock(spec=AbstractLoginUseCase)
        return mock

    @provide(scope=Scope.APP)
    async def provide_authenticate_use_case(self) -> AbstractAuthenticateUseCase:
        mock = Mock(spec=AbstractAuthenticateUseCase)
        mock.execute.return_value = self.user
        return mock

    @provide(scope=Scope.APP)
    async def provide_logout_use_case(self) -> AbstractLogoutUseCase:
        mock = Mock(spec=AbstractLogoutUseCase)
        return mock
