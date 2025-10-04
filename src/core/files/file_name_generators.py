import secrets
import time
import uuid
from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass


class FileNameGenerator(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, folder: str | None = None) -> str:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class UUIDFileNameGenerator(FileNameGenerator):
    generator: Callable[[], uuid.UUID] = uuid.uuid4

    def __call__(self, folder: str | None = None) -> str:
        path = "/".join([(folder or "").strip("/"), self.generator().hex])
        return path.removeprefix("/")


@dataclass(kw_only=True, slots=True, frozen=True)
class TimestampFileNameGenerator(FileNameGenerator):
    random_suffix_length: int = 4
    random_generator: Callable[[int], str] = secrets.token_hex

    def __call__(self, folder: str | None = None) -> str:
        timestamp = int(time.time() * 1_000_000)  # микросекунды
        random_suffix = self.random_generator(self.random_suffix_length)
        file_name = f"{timestamp}_{random_suffix}"
        path = "/".join([(folder or "").strip("/"), file_name])
        return path.removeprefix("/")
