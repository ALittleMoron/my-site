from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette

from config.constants import constants
from config.settings import settings
from entrypoints.admin.auth.backends import AdminAuthenticationBackend
from entrypoints.admin.registry import get_admin_views


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
