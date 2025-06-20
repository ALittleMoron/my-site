from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager

from dishka.integrations.starlette import setup_dishka as setup_diska_starlette
from litestar import Litestar, asgi
from litestar.handlers.asgi_handlers import ASGIRouteHandler
from litestar.openapi.config import OpenAPIConfig
from litestar.plugins import PluginProtocol
from litestar.plugins.pydantic import PydanticPlugin
from litestar.types import ControllerRouterHandler
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette
from verbose_http_exceptions.ext.litestar import ALL_EXCEPTION_HANDLERS_MAP

from config.constants import constants
from config.settings import settings
from entrypoints.admin.registry import get_admin_views
from entrypoints.api.routers import api_router
from entrypoints.auth.backends import AdminAuthenticationBackend
from ioc.container import container

Lifespan = Sequence[Callable[[Litestar], AbstractAsyncContextManager] | AbstractAsyncContextManager]


def create_admin_asgi_app(engine: AsyncEngine) -> ASGIRouteHandler:
    starlette_app = Starlette()
    admin = Admin(
        app=starlette_app,
        base_url="/",
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
    setup_diska_starlette(container=container, app=admin.admin)
    setup_diska_starlette(container=container, app=starlette_app)
    return asgi("/admin", is_mount=True, copy_scope=True)(starlette_app)


def create_litestar(
    route_handlers: Sequence[ControllerRouterHandler],
    lifespan: Lifespan,
    extra_plugins: Sequence[PluginProtocol] | None = None,
) -> Litestar:
    return Litestar(
        route_handlers,
        lifespan=lifespan,
        exception_handlers=ALL_EXCEPTION_HANDLERS_MAP,
        plugins=[PydanticPlugin(prefer_alias=True), *(extra_plugins or [])],
        openapi_config=OpenAPIConfig(
            title="docs",
            version="0.1.0",
            # TODO: check openapi json and yaml files location
            path="/api/docs",
        ),
    )


def create_base_app(lifespan: Lifespan) -> Litestar:
    return create_litestar([api_router], lifespan=lifespan)


def check_certs_exists() -> None:
    if not (constants.dir.certs_path / "public.pem").exists():
        msg = "Public key certificate file does not exists."
        raise RuntimeError(msg)
    if not (constants.dir.certs_path / "private.pem").exists():
        msg = "Secret key certificate file does not exists."
        raise RuntimeError(msg)
