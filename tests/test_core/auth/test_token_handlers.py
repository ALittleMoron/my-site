from unittest.mock import patch

import binascii
import pyseto
import pytest
import pytest_asyncio

from core.auth.enums import RoleEnum
from core.auth.exceptions import UnauthorizedError
from core.auth.schemas import AuthTokenPayload
from core.auth.token_handlers import TokenHandler, PasetoTokenHandler
from core.schemas import Secret
from tests.mocks.providers.auth import test_public_key_pem, test_private_key_pem


class TestTokenHandler:
    def test_valid_payload_not_valid_payload_fields(self) -> None:
        payload_dict = {"password": "test", "field": "test"}
        assert TokenHandler.validate_payload_dict(payload_dict) is False

    def test_valid_payload_username_not_str(self) -> None:
        payload_dict = {"username": 25, "role": "admin"}
        assert TokenHandler.validate_payload_dict(payload_dict) is False

    def test_valid_payload_role_not_str(self) -> None:
        payload_dict = {"username": "test", "role": 25}
        assert TokenHandler.validate_payload_dict(payload_dict) is False

    def test_valid_payload_role_not_in_role_enum(self) -> None:
        payload_dict = {"username": "test", "role": "TEST"}
        assert TokenHandler.validate_payload_dict(payload_dict) is False

    def test_valid_payload(self) -> None:
        payload_dict = {"username": "test", "role": "admin"}
        assert TokenHandler.validate_payload_dict(payload_dict) is True


class TestPasetoTokenHandler:
    @pytest_asyncio.fixture(autouse=True, loop_scope="session")
    async def setup(self) -> None:
        self.auth_handler = PasetoTokenHandler(
            public_key_pem=Secret(test_public_key_pem),
            secret_key_pem=Secret(test_private_key_pem),
            token_expire_seconds=1,
        )

    def test_decode_token_not_valid_payload(self) -> None:
        token = pyseto.encode(key=self.auth_handler._create_secret_key(), payload={"test": "test"})
        with pytest.raises(UnauthorizedError):
            self.auth_handler.decode_token(token)

    @pytest.mark.parametrize(
        "error", [pyseto.DecryptError, pyseto.VerifyError, binascii.Error, ValueError]
    )
    def test_decode_token_pyseto_decode_errors(self, error: type[Exception]) -> None:
        token = pyseto.encode(
            key=self.auth_handler._create_secret_key(),
            payload=AuthTokenPayload(username="TEST", role=RoleEnum.ADMIN).to_dict(),
        )
        with patch("pyseto.decode", side_effect=error):
            with pytest.raises(UnauthorizedError):
                self.auth_handler.decode_token(token)

    def test_decode_token(self) -> None:
        token = pyseto.encode(
            key=self.auth_handler._create_secret_key(),
            payload=AuthTokenPayload(username="TEST", role=RoleEnum.ADMIN).to_dict(),
        )
        decoded_token = self.auth_handler.decode_token(token)
        assert decoded_token.to_dict() == {
            "username": "TEST",
            "role": RoleEnum.ADMIN,
        }
