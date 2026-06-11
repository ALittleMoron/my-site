from litestar import Router

from entrypoints.litestar.api.account.endpoints import api_router as account_router
from entrypoints.litestar.api.auth.endpoints import api_router as auth_router
from entrypoints.litestar.api.competency_matrix.endpoints import (
    admin_router as competency_matrix_admin_router,
)
from entrypoints.litestar.api.competency_matrix.endpoints import (
    api_router as competency_matrix_router,
)
from entrypoints.litestar.api.contacts.endpoints import api_router as contacts_router
from entrypoints.litestar.api.files.endpoints import admin_router as files_admin_router
from entrypoints.litestar.api.healthcheck.endpoints import api_router as healthcheck_router
from entrypoints.litestar.api.i18n.endpoints import api_router as i18n_router
from entrypoints.litestar.api.notes.endpoints import admin_router as notes_admin_router
from entrypoints.litestar.api.notes.endpoints import api_router as notes_router
from entrypoints.litestar.api.wiki_links.endpoints import admin_router as wiki_links_admin_router

admin_api_router = Router(
    "/admin",
    route_handlers=[
        competency_matrix_admin_router,
        files_admin_router,
        notes_admin_router,
        wiki_links_admin_router,
    ],
    tags=["admin api"],
)

api_router = Router(
    "/api",
    route_handlers=[
        healthcheck_router,
        i18n_router,
        competency_matrix_router,
        contacts_router,
        auth_router,
        account_router,
        notes_router,
        admin_api_router,
    ],
    tags=["api"],
)
