import uvicorn
from dishka.integrations.starlette import setup_dishka as setup_dishka_starlette
from litestar import Litestar
from starlette.applications import Starlette

from config.initializers import (
    before_app_create,
)
from config.loggers import logger
from config.settings import settings
from db.meta import engine
from entrypoints.admin.initializers import create_admin_starlette_app
from entrypoints.litestar.api.routers import api_router
from entrypoints.litestar.cli.plugins import CLIPlugin
from entrypoints.litestar.initializers import create_litestar
from entrypoints.litestar.lifespan import app_lifespan
from entrypoints.litestar.views.routers import views_router
from ioc.container import container


def create_cli_app() -> Litestar:
    return create_litestar(
        route_handlers=[],
        lifespan=[app_lifespan],
        extra_plugins=[CLIPlugin()],
    )


def create_admin_app() -> Starlette:
    before_app_create()
    app = Starlette()
    admin = create_admin_starlette_app(app=app, engine=engine)
    setup_dishka_starlette(container=container, app=admin.admin)
    setup_dishka_starlette(container=container, app=app)
    return app


def create_app() -> Litestar:
    return create_litestar(
        route_handlers=[api_router, views_router],
        lifespan=[app_lifespan],
    )


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
