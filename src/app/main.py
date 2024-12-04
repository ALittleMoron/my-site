import uvicorn
from litestar import Litestar
from litestar.plugins.base import InitPluginProtocol
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyInitPlugin

from app.api.router import router as api_router
from app.config import settings
from app.openapi import openapi_config


def get_plugins() -> list[InitPluginProtocol]:
    config = SQLAlchemyAsyncConfig(connection_string="")
    sqlalchemy_plugin = SQLAlchemyInitPlugin(config=config)
    return [sqlalchemy_plugin]


def create_app(plugins: list[InitPluginProtocol] | None = None) -> Litestar:
    return Litestar(
        route_handlers=[api_router],
        openapi_config=openapi_config,
        plugins=plugins,
    )


def start_service() -> None:
    uvicorn.run(
        create_app(plugins=get_plugins()),
        host=settings.app.host,
        port=settings.app.port,
    )


if __name__ == "__main__":
    start_service()
