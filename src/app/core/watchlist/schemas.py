from dataclasses import dataclass

from app.core.watchlist.enums import (
    WatchListElementKind,
    WatchListElementStatus,
    WatchListElementType,
)


@dataclass(kw_only=True)
class WatchListElement:
    name: str
    native_name: str | None
    description: str | None
    my_opinion: str | None
    score: int | None
    kind: WatchListElementKind | None
    repeat_view_count: int
    status: WatchListElementStatus
    type: WatchListElementType


@dataclass(kw_only=True)
class WatchList:
    elements: list[WatchListElement]
