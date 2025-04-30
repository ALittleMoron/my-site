from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(kw_only=False, frozen=True, slots=True)
class Secret(Generic[T]):
    __value: T

    def get_secret_value(self) -> T:
        return self.__value

    def __str__(self) -> str:  # pragma: no cover
        return "SECRET-VALUE"

    def __repr__(self) -> str:  # pragma: no cover
        return "<Secret instance>"


@dataclass(frozen=True, slots=True, kw_only=True)
class ValuedDataclass(Generic[T]):
    values: list[T]

    def __len__(self) -> int:  # pragma: no cover
        return len(self.values)

    def __iter__(self) -> Iterator[T]:  # pragma: no cover
        return iter(self.values)

    def __getitem__(self, idx: int, /) -> T:
        return self.values[idx]
