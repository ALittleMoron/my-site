from unittest.mock import Mock

import pytest
from litestar.middleware import AuthenticationResult

from core.auth.enums import RoleEnum
from core.auth.exceptions import UnauthorizedError
from entrypoints.litestar.auth import AuthenticationMiddleware
from tests.fixtures import ContainerFixture, FactoryFixture


class TestAuthenticationMiddleware(ContainerFixture, FactoryFixture):
    @pytest.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_authenticate_use_case()
        self.middleware = AuthenticationMiddleware(
            app=Mock(),
            token_header_name="Authorization",
            token_prefix="Bearer",
            container=self.container.container,
        )

    async def test_authenticate_no_token(self) -> None:
        connection_mock = Mock()
        connection_mock.headers = {}
        with pytest.raises(UnauthorizedError):
            await self.middleware.authenticate_request(connection=connection_mock)

    async def test_authenticate_token_not_startswith_prefix(self) -> None:
        connection_mock = Mock()
        connection_mock.headers = {"Authorization": "INVALID token"}
        with pytest.raises(UnauthorizedError):
            await self.middleware.authenticate_request(connection=connection_mock)

    async def test_authenticate(self) -> None:
        self.use_case.execute.return_value = self.factory.core.jwt_user(
            username="test",
            role=RoleEnum.ADMIN,
        )
        connection_mock = Mock()
        connection_mock.headers = {"Authorization": "Bearer token"}
        result = await self.middleware.authenticate_request(connection=connection_mock)
        assert result == AuthenticationResult(
            user=self.factory.core.jwt_user(username="test", role=RoleEnum.ADMIN),
            auth="Bearer token",
        )
