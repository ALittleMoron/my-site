from dishka.integrations.fastapi import setup_dishka as setup_diska_fastapi
from dishka.integrations.starlette import setup_dishka as setup_diska_starlette
from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.types import Lifespan
from verbose_http_exceptions.ext.fastapi import apply_all_handlers

from config.settings import settings
from db.utils import migrate
from entrypoints.admin.registry import get_admin_views
from entrypoints.api.routers import api_router
from entrypoints.auth.backends import AdminAuthenticationBackend
from ioc.container import container


def create_admin(
    app: FastAPI,
    engine: AsyncEngine,
) -> Admin:
    admin = Admin(
        app=app,
        engine=engine,
        logo_url=settings.get_minio_object_url(
            bucket=settings.minio.bucket_names.static,
            object_path=settings.minio.static_files.logo_dark,
        ),
        favicon_url=settings.get_minio_object_url(
            bucket=settings.minio.bucket_names.static,
            object_path=settings.minio.static_files.favicon,
        ),
        authentication_backend=AdminAuthenticationBackend(
            secret_key=settings.app.secret_key.get_secret_value(),
        ),
    )
    for view in get_admin_views():
        admin.add_view(view=view)
    setup_diska_starlette(container=container, app=admin.admin)
    return admin


def create_base_app(lifespan: Lifespan[FastAPI] | None = None) -> FastAPI:
    app = FastAPI(lifespan=lifespan, docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.include_router(api_router)
    apply_all_handlers(app, override_422_openapi=True)
    return app


async def create_app(lifespan: Lifespan[FastAPI] | None = None) -> FastAPI:
    app = create_base_app(lifespan=lifespan)
    setup_diska_fastapi(container, app)
    create_admin(
        app=app,
        engine=await container.get(AsyncEngine),
    )
    migrate("head")
    return app


def check_certs_exists() -> None:
    if not (settings.dir.certs_path / "public.pem").exists():
        msg = "Public key certificate file does not exists."
        raise RuntimeError(msg)
    if not (settings.dir.certs_path / "private.pem").exists():
        msg = "Secret key certificate file does not exists."
        raise RuntimeError(msg)
