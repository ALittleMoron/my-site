from collections.abc import Callable
from typing import TypeVar

from litestar.di import Provide

T = TypeVar("T")


def provide_async(
    entity: T | Callable[[], T],
    *,
    call_entity: bool = False,
    use_cache: bool = False,
    sync_to_thread: bool | None = None,
) -> Provide:
    async def handler() -> T | Callable[[], T]:
        if call_entity and callable(entity):
            return entity()
        return entity

    return Provide(handler, use_cache=use_cache, sync_to_thread=sync_to_thread)
