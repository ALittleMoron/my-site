from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager

import sentry_sdk
from litestar import Litestar
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.logging import StructLoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.plugins import PluginProtocol
from litestar.plugins.pydantic import PydanticPlugin
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin
from litestar.static_files import create_static_files_router
from litestar.template import TemplateConfig
from litestar.types import ControllerRouterHandler, Middleware
from litestar_htmx import HTMXPlugin
from sentry_sdk.integrations.litestar import LitestarIntegration
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette
from verbose_http_exceptions.ext.litestar import ALL_EXCEPTION_HANDLERS_MAP

from config import loggers
from config.constants import constants
from config.settings import settings
from config.template_callables import register_template_callables
from db.utils import migrate
from entrypoints.admin.auth.backends import AdminAuthenticationBackend
from entrypoints.admin.registry import get_admin_views
from entrypoints.litestar.events.startup import on_startup
from entrypoints.litestar.middlewares.logging import RequestIdLoggingMiddleware

Lifespan = Sequence[Callable[[Litestar], AbstractAsyncContextManager] | AbstractAsyncContextManager]


def before_app_create() -> None:
    check_certs_exists()
    migrate("head")


def init_sentry() -> None:
    if settings.app.debug:
        # NOTE: просто не надо во время локальной разработки срать в sentry. На проде можно
        #
        # debug использую, потому что у меня нет много окружений. Только прод и локальный запуск.
        # Поэтому мне не нужно на каждый инструмент делать параметр enabled.
        return
    sentry_sdk.init(
        dsn=settings.sentry.dsn,
        send_default_pii=True,
        integrations=[LitestarIntegration()],
    )


def create_admin_starlette_app(app: Starlette, engine: AsyncEngine) -> Admin:
    admin = Admin(
        app=app,
        engine=engine,
        logo_url=settings.get_minio_object_url(
            bucket=constants.minio_buckets.static,
            object_path=constants.static_files.logo_dark,
        ),
        favicon_url=settings.get_minio_object_url(
            bucket=constants.minio_buckets.static,
            object_path=constants.static_files.favicon,
        ),
        authentication_backend=AdminAuthenticationBackend(
            secret_key=settings.app.secret_key.get_secret_value(),
        ),
    )
    for view in get_admin_views():
        admin.add_view(view=view)
    return admin


def create_litestar(
    route_handlers: Sequence[ControllerRouterHandler],
    lifespan: Lifespan,
    extra_plugins: Sequence[PluginProtocol] | None = None,
    extra_middlewares: Sequence[Middleware] | None = None,
) -> Litestar:
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
        middleware=[
            RequestIdLoggingMiddleware(),
            *(extra_middlewares or []),
        ],
        on_startup=[on_startup],
        plugins=[
            HTMXPlugin(),
            StructlogPlugin(
                config=StructlogConfig(
                    structlog_logging_config=StructLoggingConfig(
                        processors=loggers.processors,
                        wrapper_class=loggers.wrapper_class,
                        logger_factory=loggers.logger_factory,
                        cache_logger_on_first_use=loggers.cache_logger_on_first_use,
                    ),
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


def check_certs_exists() -> None:
    if not (constants.dir.certs_path / "public.pem").exists():
        msg = "Public key certificate file does not exists."
        raise RuntimeError(msg)
    if not (constants.dir.certs_path / "private.pem").exists():
        msg = "Secret key certificate file does not exists."
        raise RuntimeError(msg)
