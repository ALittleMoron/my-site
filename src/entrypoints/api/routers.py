from fastapi import APIRouter

from entrypoints.api.competency_matrix import endpoints as competency_matrix
from entrypoints.api.healthcheck import endpoints as healthcheck

api_router = APIRouter(prefix="/api", tags=["api"])
api_router.include_router(healthcheck.api_router)
api_router.include_router(competency_matrix.api_router)
