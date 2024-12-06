from collections.abc import Mapping, Sequence

import uvicorn
from litestar import Litestar
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig
from litestar.plugins.base import InitPluginProtocol
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyInitPlugin
from litestar.types import ControllerRouterHandler

from app.api.deps import dependencies
from app.api.router import router as api_router
from app.config import settings
from app.openapi import openapi_config


def get_plugins() -> list[InitPluginProtocol]:
    config = SQLAlchemyAsyncConfig(connection_string=settings.database.url.get_secret_value())
    sqlalchemy_plugin = SQLAlchemyInitPlugin(config=config)
    return [sqlalchemy_plugin]


def create_app(
    debug: bool = False,
    route_handlers: Sequence[ControllerRouterHandler] | None = None,
    openapi_configuration: OpenAPIConfig | None = None,
    plugins: list[InitPluginProtocol] | None = None,
    deps: Mapping[str, Provide] | None = None,
) -> Litestar:
    return Litestar(
        debug=debug,
        route_handlers=route_handlers if route_handlers is not None else [api_router],
        openapi_config=openapi_configuration,
        plugins=plugins,
        dependencies=deps,
    )


def start_service() -> None:
    uvicorn.run(
        create_app(
            debug=settings.app.debug,
            route_handlers=[api_router],
            openapi_configuration=openapi_config,
            plugins=get_plugins(),
            deps=dependencies,
        ),
        host=settings.app.host,
        port=settings.app.port,
    )


if __name__ == "__main__":
    start_service()
