from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, post, status_codes
from litestar.params import Body

from core.auth.enums import RoleEnum
from core.auth.types import Token
from core.auth.use_cases import AbstractLoginUseCase, AbstractLogoutUseCase
from entrypoints.litestar.api.auth.schemas import AccessTokenResponseSchema, LoginRequestSchema


class AuthApiController(Controller):
    path = "/auth"
    tags = ["auth"]

    @post(
        "/login",
        name="login-api-handler",
        description=(
            "Эндпоинт для входа в систему. Создает токен PASETO и возвращает его. В "
            "дальнейшем будет использоваться server-side сессия, а токен можно будет "
            "перезапросить новый по сессии"
        ),
        status_code=status_codes.HTTP_200_OK,
    )
    async def login(
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

    @post(
        "/logout",
        name="logout-api-handler",
        description="Эндпоинт для выхода из системы. Ничего не делает",
        status_code=status_codes.HTTP_200_OK,
    )
    async def logout(
        self,
        token: FromDishka[Token],
        use_case: FromDishka[AbstractLogoutUseCase],
    ) -> None:
        await use_case.execute(token=token)


api_router = DishkaRouter("", route_handlers=[AuthApiController])
