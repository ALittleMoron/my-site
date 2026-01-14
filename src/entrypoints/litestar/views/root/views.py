from datetime import UTC, datetime
from typing import Any

from dishka.integrations.litestar import DishkaRouter
from litestar import Request, get, status_codes
from litestar.config.response_cache import CACHE_FOREVER
from litestar.enums import MediaType
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Redirect, Response, Template

from config.settings import settings


@get("/")
async def homepage_handler() -> Response[Any]:
    return Redirect(path="/about-me/")


@get(
    "/favicon.ico",
    media_type=MediaType.TEXT,
    cache=settings.app.get_cache_duration(CACHE_FOREVER),
)
async def favicon_redirect_handler() -> Response[Any]:
    return Redirect(path=settings.get_minio_object_url(bucket="static", object_path="favicon.ico"))


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
    name="sitemap-xml-handler",
    media_type=MediaType.XML,
    cache=settings.app.get_cache_duration(CACHE_FOREVER),
)
async def sitemap_xml_handler(request: Request) -> str:
    url_template = (
        "<url>"
        "<loc>{loc}</loc>"
        "<lastmod>{lastmod}</lastmod>"
        "<changefreq>{changefreq}</changefreq>"
        "<priority>{priority}</priority>"
        "</url>"
    )
    lastmod = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    urls = "".join(
        url_template.format(loc=loc, lastmod=lastmod, changefreq=changefreq, priority=priority)
        for loc, changefreq, priority in [
            (request.url_for("about-me-index-handler"), "monthly", 1.0),
            (request.url_for("competency-matrix-questions-handler"), "daily", 0.9),
        ]
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}"
        "</urlset>"
    )


@get(
    "/sitemap",
    name="sitemap-handler",
    cache=settings.app.get_cache_duration(120),  # 2 минуты
)
async def sitemap_handler() -> Template:
    return HTMXTemplate(template_name="sitemap/index.html")


@get(
    "/.well-known/appspecific/com.chrome.devtools.json",
    name="chrome-devtools-handler",
    media_type=MediaType.JSON,
    cache=settings.app.get_cache_duration(CACHE_FOREVER),
)
async def chrome_devtools_handler() -> Response[Any]:
    return Response[Any](content={"error": "Not Found"}, status_code=status_codes.HTTP_404_NOT_FOUND)

router = DishkaRouter(
    "",
    route_handlers=[
        homepage_handler,
        favicon_redirect_handler,
        robots_txt_handler,
        sitemap_xml_handler,
        sitemap_handler,
        chrome_devtools_handler,
    ],
)
