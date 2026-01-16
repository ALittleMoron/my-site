from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, get
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template

from config.settings import settings


class BlogViewController(Controller):
    path = "/blog"

    @get(
        "",
        description="Отображение раздела блога",
        name="blog-index-handler",
        cache=settings.app.get_cache_duration(600),  # 10 минут
    )
    async def blog(self) -> Template:
        return HTMXTemplate(template_name="blog/index.html")


router = DishkaRouter("", route_handlers=[BlogViewController])
