from dishka.integrations.litestar import DishkaRouter
from litestar import get
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template

from config.settings import settings


@get(
    "",
    description="Отображение раздела блога",
    name="blog-index-handler",
    cache=settings.app.get_cache_duration(600),  # 10 минут
)
async def blog_handler() -> Template:
    return HTMXTemplate(template_name="blog/index.html")


router = DishkaRouter(
    "/blog",
    route_handlers=[blog_handler],
)
