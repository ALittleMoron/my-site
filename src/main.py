import uvicorn
from litestar import Litestar

from config.loggers import logger
from config.settings import settings
from entrypoints.litestar.initializers import create_litestar_app
from entrypoints.litestar.lifespan import app_lifespan
from ioc.container import container


def create_app() -> Litestar:
    return create_litestar_app(lifespan=[app_lifespan], container=container)


if __name__ == "__main__":
    logger.debug("Local application started", debug=settings.app.debug)
    uvicorn.run(
        app="__main__:create_app",
        host="localhost",
        port=8000,
        access_log=False,
        log_config=None,
        reload=True,
        factory=True,
    )
    logger.debug("Local application ended")
