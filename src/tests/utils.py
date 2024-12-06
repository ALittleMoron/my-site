from typing import TypeVar

from litestar.di import Provide

T = TypeVar("T")


def provide_sync(
    entity: T,
    *,
    call_entity: bool = False,
    use_cache: bool = False,
    sync_to_thread: bool | None = None,
) -> Provide:
    return Provide(
        lambda: entity() if call_entity else entity,
        use_cache=use_cache,
        sync_to_thread=sync_to_thread,
    )


def provide_async(
    entity: T,
    *,
    call_entity: bool = False,
    use_cache: bool = False,
    sync_to_thread: bool | None = None,
) -> Provide:
    async def handler() -> T:
        if call_entity:
            return entity()
        return entity

    return Provide(handler, use_cache=use_cache, sync_to_thread=sync_to_thread)
