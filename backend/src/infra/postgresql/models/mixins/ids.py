import uuid

from sqlalchemy import String, cast, func
from sqlalchemy.orm import Mapped, mapped_column


def generate_uuid4_hex() -> str:
    return uuid.uuid4().hex


class HexUuidIDMixin:
    id: Mapped[str] = mapped_column(
        String(length=32),
        primary_key=True,
        default=generate_uuid4_hex,
        server_default=func.replace(cast(func.gen_random_uuid(), String()), "-", ""),
        doc="UUIDv4 hex identifier",
    )
