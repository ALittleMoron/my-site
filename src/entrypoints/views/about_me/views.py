from dishka.integrations.litestar import DishkaRouter
from litestar import get
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template


@get(
    "",
    description="Отображение раздела Обо мне",
    name="about-me-index-handler",
)
async def about_me_handler() -> Template:
    return HTMXTemplate(template_name="about_me/index.html", context={})


router = DishkaRouter(
    "/about-me",
    route_handlers=[about_me_handler],
)
