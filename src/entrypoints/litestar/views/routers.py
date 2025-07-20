from litestar import Router

from entrypoints.litestar.views.about_me.views import router as about_me_router
from entrypoints.litestar.views.blog.views import router as blog_router
from entrypoints.litestar.views.competency_matrix.views import router as competency_matrix_router
from entrypoints.litestar.views.contacts.views import router as contacts_router
from entrypoints.litestar.views.root.views import router as root_router

views_router = Router(
    "",
    route_handlers=[
        root_router,
        about_me_router,
        competency_matrix_router,
        blog_router,
        contacts_router,
    ],
    tags=["views (Server Side Rendering endpoints)"],
)
