from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ContactMe:
    id: UUID
    name: str | None
    email: str | None
    telegram: str | None
    message: str
