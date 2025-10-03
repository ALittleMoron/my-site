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
