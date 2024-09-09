from litestar import Router

from app.api.healthcheck.endpoints import router as healthcheck_router

router = Router('/api', route_handlers=[healthcheck_router])
