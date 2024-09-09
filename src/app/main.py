import uvicorn
from litestar import Litestar

from app.api.router import router as api_router
from app.config import settings
from app.openapi import openapi_config


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[api_router],
        openapi_config=openapi_config,
    )


def start_service() -> None:
    uvicorn.run(
        create_app(),
        host=settings.app.host,
        port=settings.app.port,
    )


if __name__ == "__main__":
    start_service()
