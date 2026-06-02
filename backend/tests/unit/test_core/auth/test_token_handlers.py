# ruff: noqa: SLF001
import binascii
import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pyseto
import pytest
import pytest_asyncio

from core.auth.enums import RoleEnum
from core.auth.exceptions import UnauthorizedError
from core.auth.schemas import JwtUser
from core.auth.token_handlers import PasetoTokenHandler, TokenHandler
from core.auth.types import Token
from core.schemas import Secret
from tests.unit.mocks.providers.auth import test_private_key_pem, test_public_key_pem


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
            self.auth_handler.decode_token(Token(token))

    @pytest.mark.parametrize(
        "error",
        [pyseto.DecryptError, pyseto.VerifyError, binascii.Error, ValueError],
    )
    def test_decode_token_pyseto_decode_errors(self, error: type[Exception]) -> None:
        token = pyseto.encode(
            key=self.auth_handler._create_secret_key(),
            payload=JwtUser(username="TEST", role=RoleEnum.ADMIN).to_dict(),
        )
        with patch("pyseto.decode", side_effect=error), pytest.raises(UnauthorizedError):
            self.auth_handler.decode_token(Token(token))

    def test_decode_token(self) -> None:
        token = pyseto.encode(
            key=self.auth_handler._create_secret_key(),
            payload=JwtUser(username="TEST", role=RoleEnum.ADMIN).to_dict(),
        )
        decoded_token = self.auth_handler.decode_token(Token(token))
        assert decoded_token.to_dict() == {
            "username": "TEST",
            "role": RoleEnum.ADMIN,
        }

    def test_get_token_remaining_seconds(self) -> None:
        token = self.auth_handler.encode_token(
            payload=JwtUser(username="TEST", role=RoleEnum.ADMIN),
        )

        remaining_seconds = self.auth_handler.get_token_remaining_seconds(token)

        assert remaining_seconds is not None
        assert 0 < remaining_seconds <= self.auth_handler.token_expire_seconds

    def test_get_token_remaining_seconds_without_exp(self) -> None:
        token = pyseto.encode(
            key=self.auth_handler._create_secret_key(),
            payload=JwtUser(username="TEST", role=RoleEnum.ADMIN).to_dict(),
        )

        remaining_seconds = self.auth_handler.get_token_remaining_seconds(Token(token))

        assert remaining_seconds is None

    def test_get_token_remaining_seconds_with_expired_token(self) -> None:
        expired_at = datetime.datetime.now(tz=ZoneInfo("Etc/UTC")) - datetime.timedelta(seconds=1)
        token = pyseto.encode(
            key=self.auth_handler._create_secret_key(),
            payload={
                **JwtUser(username="TEST", role=RoleEnum.ADMIN).to_dict(),
                "exp": expired_at.isoformat(),
            },
        )

        remaining_seconds = self.auth_handler.get_token_remaining_seconds(Token(token))

        assert remaining_seconds is None
