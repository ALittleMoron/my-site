from dishka.integrations.litestar import DishkaRouter, FromDishka
from litestar import Controller, Response, get
from verbose_http_exceptions import status

from core.notes.use_cases import AbstractNotesUseCase
from entrypoints.litestar.public.discovery import PublicDiscoveryUrls, RobotsTxt, SitemapXml


class PublicDiscoveryController(Controller):
    include_in_schema = False

    @get("/sitemap.xml")
    async def sitemap(self, use_case: FromDishka[AbstractNotesUseCase]) -> Response:
        notes = await use_case.list_published_notes_for_seo()
        sitemap = SitemapXml(urls=PublicDiscoveryUrls(notes=notes).build()).render()
        return Response(
            content=sitemap,
            media_type="application/xml",
            status_code=status.HTTP_200_OK,
        )

    @get("/robots.txt")
    async def robots(self) -> Response:
        return Response(
            content=RobotsTxt().render(),
            media_type="text/plain",
            status_code=status.HTTP_200_OK,
        )


public_router = DishkaRouter(
    "",
    route_handlers=[PublicDiscoveryController],
    include_in_schema=False,
)
