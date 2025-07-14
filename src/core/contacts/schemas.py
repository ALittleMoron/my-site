from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ContactMe:
    id: UUID
    user_ip: str
    name: str | None
    email: str | None
    telegram: str | None
    message: str
