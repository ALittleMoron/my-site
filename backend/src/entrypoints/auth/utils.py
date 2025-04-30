from dataclasses import dataclass

from passlib.context import CryptContext


@dataclass(frozen=True, slots=True, kw_only=True)
class Hasher:
    context: CryptContext

    def verify_password(self, plain_password: str | bytes, hashed_password: str | bytes) -> bool:
        return self.context.verify(plain_password, hashed_password)  # type: ignore[no-any-return]

    def hash_password(self, password: str | bytes) -> str:
        return self.context.hash(password)  # type: ignore[no-any-return]
