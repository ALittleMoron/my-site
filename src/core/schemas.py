from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(kw_only=False, frozen=True, slots=True)
class Secret[T]:
    __value: T

    def get_secret_value(self) -> T:
        return self.__value

    def __str__(self) -> str:  # pragma: no cover
        return "**********"

    def __repr__(self) -> str:  # pragma: no cover
        return 'Secret("**********")'


@dataclass(frozen=True, slots=True, kw_only=True)
class ValuedDataclass[T]:
    values: list[T]

    def __len__(self) -> int:  # pragma: no cover
        return len(self.values)

    def __iter__(self) -> Iterator[T]:  # pragma: no cover
        return iter(self.values)

    def __getitem__(self, idx: int, /) -> T:  # pragma: no cover
        return self.values[idx]
