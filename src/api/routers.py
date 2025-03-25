from ninja import NinjaAPI

from api.competency_matrix.endpoints import router as competency_matrix_router
from api.healthcheck.endpoints import router as healthcheck_router

api = NinjaAPI()
api.add_router("/healthcheck/", healthcheck_router)
api.add_router("/competency-matrix/", competency_matrix_router)
