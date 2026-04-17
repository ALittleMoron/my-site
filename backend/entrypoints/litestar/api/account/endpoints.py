from core.auth.schemas import JwtUser
from core.auth.types import Token
from dishka.integrations.litestar import DishkaRouter
from entrypoints.litestar.api.account.schemas import GetBaseCurrentUserAccountResponseSchema
from litestar import Controller, Request, get
from litestar.datastructures import State


class AccountApiController(Controller):
    path = "/account"
    tags = ["account"]

    @get(
        "/base",
        name="current-user-account-api-handler",
        description=(
            "Эндпоинт для получения информации о текущем пользователе "
            "+ базовая информация об аккаунте"
        ),
    )
    async def get_base_current_user_account(
        self,
        request: Request[JwtUser, Token | None, State],
    ) -> GetBaseCurrentUserAccountResponseSchema:
        return GetBaseCurrentUserAccountResponseSchema.from_domain_schema(schema=request.user)


api_router = DishkaRouter("", route_handlers=[AccountApiController])
