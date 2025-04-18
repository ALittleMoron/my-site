from dishka.integrations.fastapi import setup_dishka
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
            object=settings.minio.static_files.logo_dark,
        ),
        favicon_url=settings.get_minio_object_url(
            bucket=settings.minio.bucket_names.static,
            object=settings.minio.static_files.favicon,
        ),
        authentication_backend=AdminAuthenticationBackend(
            secret_key=settings.app.secret_key.get_secret_value(),
            container=container,
        ),
    )
    for view in get_admin_views():
        admin.add_view(view=view)
    return admin


def create_base_app(lifespan: Lifespan[FastAPI] | None = None) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(api_router)
    apply_all_handlers(app, override_422_openapi=True)
    return app


async def create_app(lifespan: Lifespan[FastAPI] | None = None) -> FastAPI:
    app = create_base_app(lifespan=lifespan)
    setup_dishka(container, app)
    create_admin(
        app=app,
        engine=await container.get(AsyncEngine),
    )
    migrate("head")
    return app


def check_certs_exists() -> None:
    folder = settings.dir.root_path / "certs"
    if not (folder / settings.auth.public_key_pem_file_name).exists():
        msg = "Public key certificate file does not exists."
        raise RuntimeError(msg)
    if not (folder / settings.auth.secret_key_pem_file_name).exists():
        msg = "Secret key certificate file does not exists."
        raise RuntimeError(msg)
