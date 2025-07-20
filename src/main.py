from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.litestar import setup_dishka as setup_diska_fastapi
from dishka.integrations.starlette import setup_dishka as setup_diska_starlette
from litestar import Litestar
from starlette.applications import Starlette

from config.initializers import (
    before_app_create,
)
from config.loggers import logger
from db.meta import engine
from entrypoints.admin.initializers import create_admin_starlette_app
from entrypoints.litestar.api.routers import api_router
from entrypoints.litestar.cli.plugins import CLIPlugin
from entrypoints.litestar.initializers import create_litestar
from entrypoints.litestar.views.routers import views_router
from ioc.container import container


@asynccontextmanager
async def app_lifespan(app: Litestar) -> AsyncGenerator[None]:
    yield
    await app.state.dishka_container.close()


def create_cli_app() -> Litestar:
    app = create_litestar(route_handlers=[], lifespan=[], extra_plugins=[CLIPlugin()])
    setup_diska_fastapi(container, app)
    return app


def create_admin_app() -> Starlette:
    before_app_create()
    app = Starlette()
    admin = create_admin_starlette_app(app=app, engine=engine)
    setup_diska_starlette(container=container, app=admin.admin)
    setup_diska_starlette(container=container, app=app)
    return app


def create_app() -> Litestar:
    app = create_litestar(route_handlers=[api_router, views_router], lifespan=[app_lifespan])
    setup_diska_fastapi(container, app)
    return app


if __name__ == "__main__":
    logger.debug("Local application started")
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
