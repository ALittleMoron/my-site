from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager

from litestar import Litestar
from litestar.config.response_cache import ResponseCacheConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.logging import StructLoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.plugins import PluginProtocol
from litestar.plugins.pydantic import PydanticPlugin
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin
from litestar.static_files import create_static_files_router
from litestar.stores.valkey import ValkeyStore
from litestar.template import TemplateConfig
from litestar.types import ControllerRouterHandler, Middleware
from litestar_htmx import HTMXPlugin
from verbose_http_exceptions.ext.litestar import ALL_EXCEPTION_HANDLERS_MAP

from config import loggers
from config.constants import constants
from config.settings import settings
from config.template_callables import register_template_callables
from entrypoints.litestar.middlewares.logging import (
    RequestIdLoggingMiddleware,
    LogExceptionMiddleware,
)

Lifespan = Sequence[Callable[[Litestar], AbstractAsyncContextManager] | AbstractAsyncContextManager]


def create_litestar(
    route_handlers: Sequence[ControllerRouterHandler],
    lifespan: Lifespan,
    extra_plugins: Sequence[PluginProtocol] | None = None,
    extra_middlewares: Sequence[Middleware] | None = None,
) -> Litestar:
    logging_config = StructLoggingConfig(
        log_exceptions="always",
        processors=loggers.processors,
        wrapper_class=loggers.wrapper_class,
        logger_factory=loggers.logger_factory,
        cache_logger_on_first_use=loggers.cache_logger_on_first_use,
    )
    route_handlers_list = list(route_handlers)
    if settings.app.debug:
        route_handlers_list.append(
            create_static_files_router(
                path="/static",
                directories=[constants.dir.src_path / "static"],
            ),
        )
    return Litestar(
        route_handlers=route_handlers_list,
        lifespan=lifespan,
        debug=settings.app.debug,
        exception_handlers=ALL_EXCEPTION_HANDLERS_MAP,
        stores={
            "valkey": ValkeyStore.with_client(
                url=settings.valkey.url.get_secret_value(),
                db=settings.valkey.db,
                port=settings.valkey.port,
                namespace=settings.valkey.namespace,
            ),
        },
        response_cache_config=ResponseCacheConfig(store="valkey"),
        middleware=[
            RequestIdLoggingMiddleware(),
            LogExceptionMiddleware(),
            *(extra_middlewares or []),
        ],
        plugins=[
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
            *(extra_plugins or []),
        ],
        template_config=TemplateConfig(
            directory=constants.dir.src_path / "templates",
            engine=JinjaTemplateEngine,
            engine_callback=register_template_callables,
        ),
        openapi_config=OpenAPIConfig(
            title="docs",
            version="0.1.0",
            path="/api/docs",
            render_plugins=[SwaggerRenderPlugin()],
        ),
    )
