import binascii
import datetime
import json
from dataclasses import dataclass
from typing import Any
from zoneinfo import ZoneInfo

import pyseto
from verbose_http_exceptions import UnauthorizedHTTPException

from config.loggers import logger
from core.schemas import Secret
from core.users.schemas import RoleEnum
from entrypoints.admin.auth.schemas import Payload


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
class AuthHandler:
    public_key_pem: Secret[str | bytes]
    secret_key_pem: Secret[str | bytes]
    token_expire_seconds: int

    @property
    def public_key(self) -> pyseto.KeyInterface:
        return pyseto.Key.new(
            version=4,
            purpose="public",
            key=self.public_key_pem.get_secret_value(),
        )

    @property
    def secret_key(self) -> pyseto.KeyInterface:
        return pyseto.Key.new(
            version=4,
            purpose="public",
            key=self.secret_key_pem.get_secret_value(),
        )

    def prepare_payload(self, payload: Payload) -> dict[str, Any]:
        payload_dict = payload.to_dict()
        payload_dict["exp"] = (
            datetime.datetime.now(tz=ZoneInfo("Etc/UTC"))
            + datetime.timedelta(seconds=self.token_expire_seconds)
        ).isoformat()
        return payload_dict

    def decode_token(self, token: bytes) -> Payload:
        try:
            decoded = pyseto.decode(keys=self.public_key, token=token).payload
        except (pyseto.DecryptError, pyseto.VerifyError, binascii.Error, ValueError) as err:
            logger.warning(event="Pyseto decode error", exc=err, token=token)
            raise UnauthorizedHTTPException from err
        payload_dict = json.loads(decoded) if isinstance(decoded, bytes) else decoded
        if validate_payload_dict(payload_dict):
            return Payload.from_dict(payload_dict)
        logger.error(event="Decoded payload is not valid", payload=payload_dict)
        raise UnauthorizedHTTPException

    def encode_token(self, payload: Payload) -> bytes:
        return pyseto.encode(
            key=self.secret_key,
            payload=self.prepare_payload(payload),
        )
