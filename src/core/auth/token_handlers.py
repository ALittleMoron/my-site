import binascii
import datetime
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from zoneinfo import ZoneInfo

import pyseto

from config.loggers import logger
from core.auth.enums import RoleEnum
from core.auth.exceptions import UnauthorizedError
from core.auth.schemas import AuthTokenPayload
from core.schemas import Secret


class TokenHandler(ABC):
    @abstractmethod
    def decode_token(self, token: bytes) -> AuthTokenPayload:
        raise NotImplementedError

    @abstractmethod
    def encode_token(self, payload: AuthTokenPayload) -> bytes:
        raise NotImplementedError

    @staticmethod
    def validate_payload_dict(payload: dict[str, Any]) -> bool:
        payload_keys = set(payload.keys())
        required_keys = {"username", "role"}
        if (required_keys - payload_keys) != set():
            logger.error(
                event="Payload fields set is not valid",
                payload=payload,
                required_keys=required_keys,
            )
            return False
        if not isinstance(payload["username"], str):
            logger.error(event="Payload field `username` is not valid", payload=payload)
            return False
        if not isinstance(payload["role"], str) or payload["role"] not in RoleEnum:
            logger.error(event="Payload field `role` is invalid", payload=payload)
            return False
        return True


@dataclass(kw_only=True, frozen=True, slots=True)
class PasetoTokenHandler(TokenHandler):
    public_key_pem: Secret[str]
    secret_key_pem: Secret[str]
    token_expire_seconds: int

    def create_public_key(self) -> pyseto.KeyInterface:
        return pyseto.Key.new(
            version=4,
            purpose="public",
            key=self.public_key_pem.get_secret_value(),
        )

    def create_secret_key(self) -> pyseto.KeyInterface:
        return pyseto.Key.new(
            version=4,
            purpose="public",
            key=self.secret_key_pem.get_secret_value(),
        )

    def prepare_payload(self, payload: AuthTokenPayload) -> dict[str, Any]:
        payload_dict = payload.to_dict()
        payload_dict["exp"] = (
            datetime.datetime.now(tz=ZoneInfo("Etc/UTC"))
            + datetime.timedelta(seconds=self.token_expire_seconds)
        ).isoformat()
        return payload_dict

    def decode_token(self, token: bytes) -> AuthTokenPayload:
        try:
            decoded = pyseto.decode(keys=self.create_public_key(), token=token).payload
        except (pyseto.DecryptError, pyseto.VerifyError, binascii.Error, ValueError) as err:
            logger.warning(event="Pyseto decode error", exc=err, token=token)
            raise UnauthorizedError from err
        payload_dict = json.loads(decoded) if isinstance(decoded, bytes) else decoded
        if self.validate_payload_dict(payload_dict):
            return AuthTokenPayload.from_dict(payload_dict)
        logger.error(event="Decoded payload is not valid", payload=payload_dict)
        raise UnauthorizedError

    def encode_token(self, payload: AuthTokenPayload) -> bytes:
        return pyseto.encode(
            key=self.create_secret_key(),
            payload=self.prepare_payload(payload),
        )
