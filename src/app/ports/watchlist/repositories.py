from abc import ABC, abstractmethod

from app.core.watchlist.schemas import WatchList, WatchListElement


class AbstractWatchListRepository(ABC):
    @abstractmethod
    async def get_element(self, watchlist_id: int) -> WatchListElement:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> WatchList:
        raise NotImplementedError
