from abc import ABC, abstractmethod
from dataclasses import dataclass

from argon2 import PasswordHasher as Argon2CryptContext
from argon2.exceptions import VerificationError

type NeedRehash = bool
type PasswordVerified = bool


class PasswordHasher(ABC):
    @abstractmethod
    def verify_password(
        self,
        plain_password: str | bytes,
        hashed_password: str | bytes,
    ) -> tuple[PasswordVerified, NeedRehash]:
        raise NotImplementedError

    @abstractmethod
    def hash_password(self, password: str | bytes) -> str:
        raise NotImplementedError


@dataclass(frozen=True, slots=True, kw_only=True)
class Argon2PasswordHasher(PasswordHasher):
    context: Argon2CryptContext

    def verify_password(
        self,
        plain_password: str | bytes,
        hashed_password: str | bytes,
    ) -> tuple[PasswordVerified, NeedRehash]:
        hashed_password_str = (
            hashed_password if isinstance(hashed_password, str) else hashed_password.decode()
        )
        try:
            return (
                self.context.verify(hashed_password, plain_password),
                self.context.check_needs_rehash(hashed_password_str),
            )
        except VerificationError:
            return False, False

    def hash_password(self, password: str | bytes) -> str:
        return self.context.hash(password)
