from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True, kw_only=True)
class ValuedDataclass(Generic[T]):
    values: list[T]

    def __len__(self) -> int:  # pragma: no cover
        return len(self.values)

    def __iter__(self) -> Iterator[T]:  # pragma: no cover
        return iter(self.values)
