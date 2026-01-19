from abc import ABC, abstractmethod


class AbstractGenerator[T](ABC):
    @abstractmethod
    def get_next(self) -> T:
        raise NotImplementedError
