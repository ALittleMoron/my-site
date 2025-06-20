from litestar import Router

views_router = Router(
    "/",
    route_handlers=[],
    include_in_schema=False,
)
