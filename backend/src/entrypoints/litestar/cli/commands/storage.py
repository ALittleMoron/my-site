from dishka import make_async_container

from core.files.file_storages import FileStorage
from infra.ioc.registry import get_providers


async def init_buckets_command() -> None:
    command_container = make_async_container(*get_providers())
    try:
        file_storage = await command_container.get(FileStorage)
        await file_storage.init_storage()
    finally:
        await command_container.close()
