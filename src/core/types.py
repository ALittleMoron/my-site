from typing import NewType

IntId = NewType("IntId", int)


class SearchName(str):
    __slots__ = ()

    @property
    def cleaned(self) -> str:
        return self.lower().strip()
