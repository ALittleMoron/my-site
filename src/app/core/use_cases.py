from abc import ABC, abstractmethod
from typing import Any


class UseCase(ABC):
    """Abstract use case class."""

    @abstractmethod
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        """Main execute method of abstract use case."""
        raise NotImplementedError
