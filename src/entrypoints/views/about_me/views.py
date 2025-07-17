from dishka.integrations.litestar import DishkaRouter
from litestar import get
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template

from config.settings import settings


@get(
    "",
    description="Отображение раздела Обо мне",
    name="about-me-index-handler",
    cache=settings.app.get_cache_duration(600),  # 10 минут
)
async def about_me_handler() -> Template:
    return HTMXTemplate(template_name="about_me/index.html")


router = DishkaRouter(
    "/about-me",
    route_handlers=[about_me_handler],
)
