from litestar import Router, get
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template


@get("")
async def about_me_handler() -> Template:
    return HTMXTemplate(
        template_name="app/about_me.html",
        context={},
    )


router = Router(
    "/about-me/",
    route_handlers=[about_me_handler],
)
