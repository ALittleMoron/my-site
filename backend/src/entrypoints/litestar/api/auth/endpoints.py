from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, post, status_codes
from litestar.params import Body

from core.auth.enums import RoleEnum
from core.auth.types import Token
from core.auth.use_cases import AuthUseCase
from entrypoints.litestar.api.auth.schemas import AccessTokenResponseSchema, LoginRequestSchema


class AuthApiController(Controller):
    path = "/auth"
    tags = ["auth"]

    @post(
        "/login",
        name="login-api-handler",
        description=(
            "Log in to the system. Creates and returns a PASETO token. A server-side session "
            "will be used later, and the token will be refreshable through that session."
        ),
        status_code=status_codes.HTTP_200_OK,
    )
    async def login(
        self,
        data: Annotated[LoginRequestSchema, Body()],
        use_case: FromDishka[AuthUseCase],
    ) -> AccessTokenResponseSchema:
        token = await use_case.login(
            username=data.username,
            password=data.password,
            required_role=RoleEnum.MODERATOR,
        )
        return AccessTokenResponseSchema.from_domain_schema(schema=token)

    @post(
        "/logout",
        name="logout-api-handler",
        description="Log out of the system. Revokes the current PASETO token.",
        status_code=status_codes.HTTP_200_OK,
    )
    async def logout(
        self,
        token: FromDishka[Token],
        use_case: FromDishka[AuthUseCase],
    ) -> None:
        await use_case.logout(token=token)


api_router = DishkaRouter("", route_handlers=[AuthApiController])
