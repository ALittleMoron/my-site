from typing import Any

from litestar import Router, get
from litestar.config.response_cache import CACHE_FOREVER
from litestar.enums import MediaType
from litestar.response import Redirect, Response

from config.settings import settings
from entrypoints.litestar.views.about_me.views import router as about_me_router
from entrypoints.litestar.views.blog.views import router as blog_router
from entrypoints.litestar.views.competency_matrix.views import router as competency_matrix_router
from entrypoints.litestar.views.contacts.views import router as contacts_router


@get("/")
async def homepage_handler() -> Response[Any]:
    return Redirect(path="/about-me/")


@get(
    "/robots.txt",
    media_type=MediaType.TEXT,
    cache=settings.app.get_cache_duration(CACHE_FOREVER),
)
async def robots_txt_handler() -> str:
    return (
        "User-agent: *\n"
        "Allow: /about-me\n"
        "Allow: /competency-matrix\n"
        "Disallow /\n"
        f"Sitemap: {settings.get_url('sitemap.xml')}"
    )


@get(
    "/sitemap.xml",
    media_type=MediaType.XML,
    cache=settings.app.get_cache_duration(CACHE_FOREVER),
)
async def sitemap_handler() -> str:
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    sitemap += '</urlset>'
    return sitemap


views_router = Router(
    "",
    route_handlers=[
        homepage_handler,
        robots_txt_handler,
        about_me_router,
        competency_matrix_router,
        blog_router,
        contacts_router,
    ],
    tags=["views (Server Side Rendering endpoints)"],
)
