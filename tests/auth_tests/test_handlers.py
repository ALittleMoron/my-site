import pyseto
import pytest
import pytest_asyncio
from dishka import AsyncContainer
from verbose_http_exceptions import UnauthorizedHTTPException

from entrypoints.admin.auth.handlers import validate_payload_dict, AuthHandler


class TestValidatePayloadDict:
    def test_valid_payload_not_valid_payload_fields(self) -> None:
        payload_dict = {"password": "test", "field": "test"}
        assert validate_payload_dict(payload_dict) is False

    def test_valid_payload_username_not_str(self) -> None:
        payload_dict = {"username": 25, "role": "admin"}
        assert validate_payload_dict(payload_dict) is False

    def test_valid_payload_role_not_str(self) -> None:
        payload_dict = {"username": "test", "role": 25}
        assert validate_payload_dict(payload_dict) is False

    def test_valid_payload_role_not_in_role_enum(self) -> None:
        payload_dict = {"username": "test", "role": "TEST"}
        assert validate_payload_dict(payload_dict) is False

    def test_valid_payload(self) -> None:
        payload_dict = {"username": "test", "role": "admin"}
        assert validate_payload_dict(payload_dict) is True


class TestAuthHandler:
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self, container: AsyncContainer) -> None:
        self.auth_handler = await container.get(AuthHandler)

    def test_decode_token_not_valid_payload(self) -> None:
        token = pyseto.encode(key=self.auth_handler.secret_key, payload={"test": "test"})
        with pytest.raises(UnauthorizedHTTPException):
            self.auth_handler.decode_token(token)
