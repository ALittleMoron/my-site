from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from config.initializers import before_app_create
from dishka.integrations.litestar import setup_dishka as setup_dishka_litestar
from ioc.container import container
from litestar import Litestar


@asynccontextmanager
async def app_lifespan(app: Litestar) -> AsyncGenerator[None]:
    setup_dishka_litestar(container=container, app=app)
    before_app_create()
    yield
    await app.state.dishka_container.close()
