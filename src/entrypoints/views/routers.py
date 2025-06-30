from typing import Any

from litestar import Router, get
from litestar.response import Redirect, Response

from entrypoints.views.about_me.views import router as about_me_router
from entrypoints.views.competency_matrix.views import router as competency_matrix_router


@get("")
async def homepage_handler() -> Response[Any]:
    return Redirect(path="/about-me/")


views_router = Router(
    "/",
    route_handlers=[homepage_handler, about_me_router, competency_matrix_router],
    tags=["views"],
)
