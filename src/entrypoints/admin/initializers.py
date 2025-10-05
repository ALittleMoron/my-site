from functools import partial

from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from config.constants import constants
from config.settings import settings
from entrypoints.admin.auth_backends import AdminAuthenticationBackend, SessionConfig
from entrypoints.admin.registry import get_admin_views
from entrypoints.admin.routes.files import presign_put_media_file
from entrypoints.admin.template_callables import markdown_to_html


def apply_template_callables(admin: Admin) -> None:
    admin.templates.env.globals["markdown_to_html"] = markdown_to_html
    admin.templates.env.globals["settings"] = settings
    admin.templates.env.globals["constants"] = constants
    admin.templates.env.globals["get_full_url"] = settings.get_url
    admin.templates.env.globals["get_static_file_url"] = partial(
        settings.get_minio_object_url,
        bucket="static",
    )


def apply_views(admin: Admin) -> None:
    for view in get_admin_views():
        admin.add_view(view=view)


def apply_custom_inner_routes(admin: Admin) -> None:
    admin.admin.router.routes = [
        Mount("/statics", app=StaticFiles(packages=["sqladmin"]), name="statics"),
        Route("/", endpoint=admin.index, name="index"),
        Route("/{identity}/list", endpoint=admin.list, name="list"),
        Route("/{identity}/details/{pk:path}", endpoint=admin.details, name="details"),
        Route(
            "/{identity}/delete",
            endpoint=admin.delete,
            name="delete",
            methods=["DELETE"],
        ),
        Route(
            "/{identity}/create",
            endpoint=admin.create,
            name="create",
            methods=["GET", "POST"],
        ),
        Route(
            "/{identity}/edit/{pk:path}",
            endpoint=admin.edit,
            name="edit",
            methods=["GET", "POST"],
        ),
        Route("/{identity}/export/{export_type}", endpoint=admin.export, name="export"),
        Route("/{identity}/ajax/lookup", endpoint=admin.ajax_lookup, name="ajax_lookup"),
        Route(
            "/presign-put",
            endpoint=presign_put_media_file,
            name="presign-put",
            methods=["GET"],
        ),
        Route("/login", endpoint=admin.login, name="login", methods=["GET", "POST"]),
        Route("/logout", endpoint=admin.logout, name="logout", methods=["GET"]),
    ]


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
            session_config=SessionConfig(
                secret_key=settings.admin.secret_key.get_secret_value(),
            ),
        ),
        templates_dir=constants.path.template_dir.as_posix(),
    )
    apply_custom_inner_routes(admin)
    apply_views(admin)
    apply_template_callables(admin)
    return admin
