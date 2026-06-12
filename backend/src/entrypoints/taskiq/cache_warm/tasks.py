from dishka.integrations.taskiq import FromDishka, inject

from entrypoints.litestar.response_cache import ResponseCacheDomain
from entrypoints.taskiq.broker import broker
from entrypoints.taskiq.cache_warm.service import ResponseCacheWarmService
from infra.config.constants import constants
from infra.config.settings import settings


@broker.task(
    constants.taskiq.cache_warm_all_task_name,
    schedule=[
        {
            "schedule_id": constants.taskiq.cache_warm_all_task_name,
            "interval": settings.taskiq.cache_warm_interval_seconds,
        },
    ],
)
@inject(patch_module=True)
async def cache_warm_all(service: FromDishka[ResponseCacheWarmService]) -> dict[str, int]:
    return (await service.warm_all()).as_dict()


@broker.task(constants.taskiq.cache_warm_domain_task_name)
@inject(patch_module=True)
async def cache_warm_domain(
    domain_value: str,
    service: FromDishka[ResponseCacheWarmService],
) -> dict[str, int]:
    return (await service.warm_domain(domain=ResponseCacheDomain(domain_value))).as_dict()
