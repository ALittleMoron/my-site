from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, post
from litestar.params import Body

from core.auth.enums import RoleEnum
from core.auth.use_cases import AbstractLoginUseCase
from entrypoints.litestar.api.auth.schemas import AccessTokenResponseSchema, LoginRequestSchema


class AuthController(Controller):
    path = "/auth"

    @post(
        "/login",
        name="auth.login",
        description=(
            "Эндпоинт для входа в систему. Создает токен PASETO и возвращает его. В "
            "дальнейшем будет использоваться server-side сессия, а токен можно будет "
            "перезапросить новый по сессии"
        ),
    )
    async def login_handler(
        self,
        data: Annotated[LoginRequestSchema, Body()],
        use_case: FromDishka[AbstractLoginUseCase],
    ) -> AccessTokenResponseSchema:
        token = await use_case.execute(
            username=data.username,
            password=data.password,
            required_role=RoleEnum.ADMIN,  # NOTE: пока только админы могут логиниться
        )
        return AccessTokenResponseSchema.from_domain_schema(schema=token)


api_router = DishkaRouter("", route_handlers=[AuthController])
