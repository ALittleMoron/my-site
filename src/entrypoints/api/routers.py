from litestar import Router

from entrypoints.api.competency_matrix import endpoints as competency_matrix
from entrypoints.api.healthcheck import endpoints as healthcheck

api_router = Router(
    "/api",
    route_handlers=[healthcheck.api_router, competency_matrix.api_router],
    tags=["api"],
)
