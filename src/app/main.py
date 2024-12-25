from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

import uvicorn
from litestar import Litestar
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig
from litestar.plugins.base import InitPluginProtocol
from litestar.plugins.pydantic import PydanticInitPlugin
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyInitPlugin
from litestar.types import ControllerRouterHandler
from verbose_http_exceptions.ext.litestar import ALL_EXCEPTION_HANDLERS_MAP

from app.api.deps import dependencies
from app.api.router import router as api_router
from app.config import settings
from app.openapi import openapi_config

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from verbose_http_exceptions.ext.litestar.types import LitestarExceptionHandlersMap


def get_plugins() -> list[InitPluginProtocol]:
    return [
        PydanticInitPlugin(prefer_alias=True),
        SQLAlchemyInitPlugin(
            config=SQLAlchemyAsyncConfig(connection_string=settings.database.url.get_secret_value())
        ),
    ]


def create_app(  # noqa: PLR0913
    *,
    debug: bool = False,
    route_handlers: Sequence[ControllerRouterHandler] | None = None,
    openapi_configuration: OpenAPIConfig | None = None,
    plugins: list[InitPluginProtocol] | None = None,
    deps: Mapping[str, Provide] | None = None,
    exception_handlers: "LitestarExceptionHandlersMap | None" = None,
) -> Litestar:
    return Litestar(
        debug=debug,
        route_handlers=route_handlers if route_handlers is not None else [api_router],
        openapi_config=openapi_configuration,
        plugins=plugins,
        dependencies=deps,
        exception_handlers=exception_handlers,
    )


def create_default_app() -> Litestar:
    return create_app(
        debug=settings.app.debug,
        route_handlers=[api_router],
        openapi_configuration=openapi_config,
        plugins=get_plugins(),
        deps=dependencies,
        exception_handlers=ALL_EXCEPTION_HANDLERS_MAP,
    )


def start_service() -> None:
    uvicorn.run(
        create_default_app(),
        host=settings.app.host,
        port=settings.app.port,
    )


if __name__ == "__main__":
    start_service()
