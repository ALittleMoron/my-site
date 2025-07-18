from litestar import Router

from entrypoints.litestar.api.competency_matrix.endpoints import (
    api_router as competency_matrix_router,
)
from entrypoints.litestar.api.contacts.endpoints import api_router as contacts_router
from entrypoints.litestar.api.healthcheck.endpoints import api_router as healthcheck_router

api_router = Router(
    "/api",
    route_handlers=[
        healthcheck_router,
        competency_matrix_router,
        contacts_router,
    ],
    tags=["api"],
)
