from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, Request, get
from litestar.datastructures import State
from litestar_htmx import ClientRedirect, HTMXTemplate

from core.auth.schemas import JwtUser
from core.auth.types import Token


class AuthViewController(Controller):
    path = "/auth"

    @get(
        "/login",
        description="Страница авторизации",
        name="login-form-handler",
    )
    async def login(self, request: Request[JwtUser, Token, State]) -> HTMXTemplate | ClientRedirect:
        if request.user.is_anon:
            return HTMXTemplate(
                re_swap="afterbegin",
                re_target="#login_form_modal",
                template_name="auth/login.html",
            )
        return ClientRedirect(redirect_to=request.headers.get("referer", "/"))

    @get(
        "/logout",
        description="Выход из системы",
        name="logout-handler",
    )
    async def logout(self, request: Request) -> ClientRedirect:
        # TODO: real logout
        return ClientRedirect(redirect_to=request.headers.get("referer", "/"))


router = DishkaRouter("", route_handlers=[AuthViewController])
