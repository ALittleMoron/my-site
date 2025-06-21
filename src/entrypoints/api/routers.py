from litestar import Router

from entrypoints.api.competency_matrix.endpoints import api_router as competency_matrix_router
from entrypoints.api.healthcheck.endpoints import api_router as healthcheck_router

api_router = Router(
    "/api",
    route_handlers=[healthcheck_router, competency_matrix_router],
    tags=["api"],
)
