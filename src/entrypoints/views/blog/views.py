from dishka.integrations.litestar import DishkaRouter
from litestar import get
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template


@get(
    "",
    description="Отображение раздела блога",
    name="blog-index-handler",
)
async def blog_handler() -> Template:
    return HTMXTemplate(template_name="blog/index.html", context={})


router = DishkaRouter(
    "/blog",
    route_handlers=[blog_handler],
)
