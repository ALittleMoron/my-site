from unittest.mock import Mock

from dishka import Provider, BaseScope, Component, provide, Scope

from config.settings import Settings
from core.auth.enums import RoleEnum
from core.auth.password_hashers import PasswordHasher
from core.auth.schemas import JwtUser
from core.auth.storages import AuthStorage
from core.auth.token_handlers import TokenHandler
from core.auth.use_cases import AbstractLoginUseCase, AbstractAuthenticateUseCase

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
    async def provide_hasher(self) -> PasswordHasher:
        mock = Mock(spec=PasswordHasher)
        mock.verify_password.return_value = True, False
        mock.hash_password.return_value = "1234"
        return mock

    @provide(scope=Scope.APP)
    async def provide_token_handler(self) -> TokenHandler:
        mock = Mock(spec=TokenHandler)
        mock.encode_token.return_value = "TOKEN".encode()
        mock.decode_token.return_value = JwtUser(username="test", role=RoleEnum.ADMIN)
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
        return mock
