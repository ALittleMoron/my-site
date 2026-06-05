from litestar import Litestar

from entrypoints.litestar.response_cache import invalidate_all_response_cache_domains
from infra.config.loggers import logger


async def invalidate_cache_command(app: Litestar) -> None:
    await invalidate_all_response_cache_domains(app=app)
    logger.info("Response cache invalidated.")
