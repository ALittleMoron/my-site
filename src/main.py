import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.litestar import setup_dishka as setup_diska_fastapi
from litestar import Litestar
from sqlalchemy.ext.asyncio import AsyncEngine

from config.initializers import check_certs_exists, create_admin_asgi_app, create_litestar
from config.settings import settings
from db.utils import migrate
from entrypoints.api.routers import api_router
from entrypoints.cli.plugins import CLIPlugin
from ioc.container import container


@asynccontextmanager
async def app_lifespan(app: Litestar) -> AsyncGenerator[None]:
    yield
    await app.state.dishka_container.close()


def create_cli_app() -> Litestar:
    app = create_litestar(route_handlers=[], lifespan=[], extra_plugins=[CLIPlugin()])
    setup_diska_fastapi(container, app)
    migrate("head")
    return app


async def create_app() -> Litestar:
    admin = create_admin_asgi_app(engine=await container.get(AsyncEngine))
    app = create_litestar(route_handlers=[api_router, admin], lifespan=[app_lifespan])
    setup_diska_fastapi(container, app)
    migrate("head")
    return app


if __name__ == "__main__":
    check_certs_exists()
    app = asyncio.run(create_app())
    uvicorn.run(
        app=app,
        host=settings.app.host,
        port=settings.app.port,
        access_log=False,
    )
