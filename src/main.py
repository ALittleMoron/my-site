from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.litestar import setup_dishka as setup_diska_fastapi
from dishka.integrations.starlette import setup_dishka as setup_diska_starlette
from litestar import Litestar
from starlette.applications import Starlette

from config.initializers import check_certs_exists, create_admin_starlette_app, create_litestar
from db.meta import engine
from db.utils import migrate
from entrypoints.api.routers import api_router
from entrypoints.cli.plugins import CLIPlugin
from entrypoints.views.routers import views_router
from ioc.container import container


@asynccontextmanager
async def app_lifespan(app: Litestar) -> AsyncGenerator[None]:
    yield
    await app.state.dishka_container.close()


def create_cli_app() -> Litestar:
    check_certs_exists()
    app = create_litestar(route_handlers=[], lifespan=[], extra_plugins=[CLIPlugin()])
    setup_diska_fastapi(container, app)
    migrate("head")
    return app


def create_admin_app() -> Starlette:
    check_certs_exists()
    app = Starlette()
    admin = create_admin_starlette_app(app=app, engine=engine)
    setup_diska_starlette(container=container, app=admin.admin)
    setup_diska_starlette(container=container, app=app)
    return app


def create_app() -> Litestar:
    check_certs_exists()
    app = create_litestar(route_handlers=[views_router, api_router], lifespan=[app_lifespan])
    setup_diska_fastapi(container, app)
    migrate("head")
    return app


if __name__ == "__main__":
    uvicorn.run(app=create_app(), host="localhost", port=8000, access_log=False)
