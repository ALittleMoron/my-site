from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette

from config.constants import constants
from config.settings import settings
from entrypoints.admin.auth_backends import AdminAuthenticationBackend
from entrypoints.admin.registry import get_admin_views
from entrypoints.admin.template_callables import markdown_to_html


def apply_template_callables(admin: Admin) -> None:
    admin.templates.env.globals["markdown_to_html"] = markdown_to_html


def apply_views(admin: Admin) -> None:
    for view in get_admin_views():
        admin.add_view(view=view)


def create_admin_starlette_app(app: Starlette, engine: AsyncEngine) -> Admin:
    admin = Admin(
        app=app,
        title="Админ-панель",
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
        templates_dir=constants.path.template_dir.as_posix(),
    )
    apply_views(admin)
    apply_template_callables(admin)
    return admin
