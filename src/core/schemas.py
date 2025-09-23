from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(kw_only=False, frozen=True, slots=True)
class Secret[T]:
    __value: T

    def get_secret_value(self) -> T:
        return self.__value

    def __str__(self) -> str:
        return "**********"

    def __repr__(self) -> str:
        return 'Secret("**********")'


@dataclass(frozen=True, slots=True, kw_only=True)
class ValuedDataclass[T]:
    values: list[T]

    def __len__(self) -> int:
        return len(self.values)

    def __iter__(self) -> Iterator[T]:
        return iter(self.values)

    def __getitem__(self, idx: int, /) -> T:
        return self.values[idx]
