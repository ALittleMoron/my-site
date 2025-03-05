from litestar import Router

from app.views.competency_matrix.endpoints import router as competency_matrix_router
from app.views.healthcheck.endpoints import router as healthcheck_router

router = Router('/api', route_handlers=[healthcheck_router, competency_matrix_router])
