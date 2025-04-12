from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI
from verbose_http_exceptions import BaseVerboseHTTPException

from api.competency_matrix.endpoints import router as competency_matrix_router
from api.healthcheck.endpoints import router as healthcheck_router

ninja_app = NinjaAPI()
ninja_app.add_router("/healthcheck/", healthcheck_router)
ninja_app.add_router("/competency-matrix/", competency_matrix_router)


@ninja_app.exception_handler(BaseVerboseHTTPException)
def base_exception_handler(request: HttpRequest, exc: BaseVerboseHTTPException) -> HttpResponse:
    return ninja_app.create_response(request=request, data=exc.as_dict(), status=exc.status_code)
