# ruff: noqa: S106
import pytest_asyncio

from core.auth.enums import RoleEnum
from core.auth.schemas import (
    AccessTokenResult,
    AuthLoginParams,
    AuthLoginResult,
    AuthSessionCredentials,
)
from core.auth.types import SessionSecret, Token
from tests.test_cases import ApiTestCase
from tests.unit.mocks.providers.auth import test_current_datetime


class TestLoginAPI(ApiTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.uuid = await self.container.get_random_uuid()
        self.use_case = await self.container.get_auth_use_case()

    def test_login(self) -> None:
        self.use_case.login.return_value = AuthLoginResult(
            access_token=AccessTokenResult(token=Token(b"ACCESS"), expires_in_seconds=900),
            session=AuthSessionCredentials(
                secret=SessionSecret("session-secret"),
                expires_in_seconds=2_592_000,
            ),
        )

        response = self.api.post_login(
            data=self.factory.api.login_request(
                username="USERNAME",
                password="PASSWORD",
            ),
        )

        assert response.json() == {
            "accessToken": "ACCESS",
            "accessTokenExpiresInSeconds": 900,
        }
        set_cookie = response.headers["set-cookie"]
        assert "__Secure-msid=session-secret" in set_cookie
        assert "HttpOnly" in set_cookie
        assert "Secure" in set_cookie
        assert "SameSite=lax" in set_cookie
        assert "Path=/api/auth" in set_cookie
        assert "Max-Age=2592000" in set_cookie
        self.use_case.login.assert_called_once_with(
            params=AuthLoginParams(
                username="USERNAME",
                password="PASSWORD",
                required_role=RoleEnum.MODERATOR,
                current_datetime=test_current_datetime,
            ),
        )
