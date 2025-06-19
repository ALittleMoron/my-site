import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from config.initializers import check_certs_exists, create_app
from config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await app.state.dishka_container.close()


if __name__ == "__main__":
    check_certs_exists()
    app = asyncio.run(create_app(lifespan=lifespan))
    uvicorn.run(
        app=app,
        host=settings.app.host,
        port=settings.app.port,
        access_log=False,
    )
