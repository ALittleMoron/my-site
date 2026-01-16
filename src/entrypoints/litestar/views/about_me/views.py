from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, get
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template

from config.settings import settings


class AboutMeViewController(Controller):
    path = "/about-me"

    @get(
        "",
        description="Отображение раздела Обо мне",
        name="about-me-index-handler",
        cache=settings.app.get_cache_duration(600),  # 10 минут
    )
    async def about_me(self) -> Template:
        return HTMXTemplate(template_name="about_me/index.html")


router = DishkaRouter("", route_handlers=[AboutMeViewController])
