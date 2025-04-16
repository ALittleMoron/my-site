from dataclasses import dataclass
from typing import Any

from core.auth.schemas import RoleEnum


@dataclass(kw_only=True)
class Payload:
    username: str
    role: RoleEnum

    def to_dict(self) -> dict[str, Any]:
        return {"username": self.username, "role": self.role.value}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Payload":
        return cls(
            username=payload['username'],
            role=RoleEnum(payload['role']),
        )
