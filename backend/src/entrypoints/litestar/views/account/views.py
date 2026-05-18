from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, get
from litestar.response import Template
from litestar_htmx import HTMXTemplate


class AccountViewController(Controller):
    path = "/account"

    @get(
        "/navbar-account-info",
        name="navbar-account-info-handler",
        description="Отображение информации о текущем пользователе в шапке",
    )
    async def get_navbar_account_info(self) -> Template:
        return HTMXTemplate(template_name="account/blocks/navbar_account_info.html")


router = DishkaRouter("", route_handlers=[AccountViewController])
