from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager

from dishka import AsyncContainer
from litestar import Litestar, Router
from litestar.config.response_cache import ResponseCacheConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.logging import StructLoggingConfig
from litestar.middleware import DefineMiddleware
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.plugins import PluginProtocol
from litestar.plugins.pydantic import PydanticPlugin
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin
from litestar.static_files import create_static_files_router
from litestar.stores.base import Store
from litestar.stores.valkey import ValkeyStore
from litestar.template import TemplateConfig
from litestar.types import Middleware
from litestar_htmx import HTMXPlugin
from verbose_http_exceptions.ext.litestar import ALL_EXCEPTION_HANDLERS_MAP

from config import loggers
from config.constants import constants
from config.settings import settings
from entrypoints.litestar.api.routers import api_router
from entrypoints.litestar.auth import AuthenticationMiddleware
from entrypoints.litestar.cli.plugins import CLIPlugin
from entrypoints.litestar.middlewares.logging import (
    LogExceptionMiddleware,
    RequestIdLoggingMiddleware,
)
from entrypoints.litestar.template_callables import register_template_callables
from entrypoints.litestar.views.routers import views_router

Lifespan = Sequence[Callable[[Litestar], AbstractAsyncContextManager] | AbstractAsyncContextManager]


def create_stores() -> dict[str, Store]:
    return {
        **(
            {
                "litestar_cache": ValkeyStore.with_client(
                    url=settings.valkey.url_for_http_cache.get_secret_value(),
                    db=constants.valkey.databases.response_cache,
                    port=settings.valkey.port,
                    namespace=constants.valkey.namespaces.framework,
                ),
            }
            if settings.app.use_cache
            else {}
        ),
    }


def create_openapi_config() -> OpenAPIConfig:
    return OpenAPIConfig(
        title="docs",
        version="0.1.0",
        path="/api/docs",
        render_plugins=[SwaggerRenderPlugin()],
    )


def create_template_config() -> TemplateConfig:
    return TemplateConfig(
        directory=constants.path.template_dir / "application",
        engine=JinjaTemplateEngine,
        engine_callback=register_template_callables,
    )


def create_plugins() -> list[PluginProtocol]:
    logging_config = StructLoggingConfig(
        log_exceptions="always",
        processors=loggers.processors,
        wrapper_class=loggers.wrapper_class,
        logger_factory=loggers.logger_factory,
        cache_logger_on_first_use=loggers.cache_logger_on_first_use,
    )
    return [
        HTMXPlugin(),
        StructlogPlugin(
            config=StructlogConfig(
                structlog_logging_config=logging_config,
                middleware_logging_config=LoggingMiddlewareConfig(
                    request_log_fields=["path", "method", "query", "path_params"],
                    response_log_fields=["status_code"],
                ),
            ),
        ),
        PydanticPlugin(prefer_alias=True),
    ]


def create_middlewares(container: AsyncContainer) -> list[Middleware]:
    return [
        RequestIdLoggingMiddleware(),
        LogExceptionMiddleware(),
        DefineMiddleware(
            AuthenticationMiddleware,
            token_header_name=settings.auth.token_header_name,
            token_prefix=settings.auth.token_prefix,
            container=container,
            exclude=["/api/docs", "/static"],
        ),
    ]


def create_routers() -> list[Router]:
    routers = [api_router, views_router]
    if settings.app.debug:
        routers.append(
            create_static_files_router(
                path="/static",
                directories=[constants.path.src_dir / "static"],
            ),
        )
    return routers


def create_cli_app(
    lifespan: Lifespan,
) -> Litestar:
    return Litestar(
        lifespan=lifespan,
        debug=settings.app.debug,
        exception_handlers=ALL_EXCEPTION_HANDLERS_MAP,
        stores=create_stores(),
        plugins=[CLIPlugin()],
        template_config=create_template_config(),
        openapi_config=create_openapi_config(),
    )


def create_litestar_app(
    lifespan: Lifespan,
    container: AsyncContainer,
    extra_plugins: Sequence[PluginProtocol] | None = None,
    extra_middlewares: Sequence[Middleware] | None = None,
) -> Litestar:
    return Litestar(
        route_handlers=create_routers(),
        lifespan=lifespan,
        debug=settings.app.debug,
        exception_handlers=ALL_EXCEPTION_HANDLERS_MAP,
        stores=create_stores(),
        response_cache_config=(
            ResponseCacheConfig(store="litestar_cache") if settings.app.use_cache else None
        ),
        middleware=[*create_middlewares(container), *(extra_middlewares or [])],
        plugins=[*create_plugins(), *(extra_plugins or [])],
        template_config=create_template_config(),
        openapi_config=create_openapi_config(),
    )
