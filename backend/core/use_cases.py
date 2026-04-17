from abc import ABC, abstractmethod
from typing import Any


class UseCase(ABC):
    """Abstract use case class."""

    @abstractmethod
    async def execute(self, *_: Any, **__: Any) -> Any:  # noqa: ANN401
        """Main execute method of abstract use case."""
        raise NotImplementedError
