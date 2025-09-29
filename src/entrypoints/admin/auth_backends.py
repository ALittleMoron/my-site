from typing import TYPE_CHECKING, Self

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import Response

from config.loggers import logger
from core.auth.enums import RoleEnum
from core.auth.use_cases import AbstractAuthenticateUseCase, AbstractLoginUseCase

if TYPE_CHECKING:
    from dishka import AsyncContainer


class AdminAuthenticationBackend(AuthenticationBackend):
    async def login(self: Self, request: Request) -> bool:
        request_container: AsyncContainer = request.state.dishka_container
        login_use_case = await request_container.get(AbstractLoginUseCase)
        form = await request.form()
        username, password = form["username"], form["password"]
        if not isinstance(username, str) or not isinstance(password, str):
            logger.warning(
                "username or password is not str",
                username=username,
                password=password,
            )
            return False
        token = await login_use_case.execute(
            username=username,
            password=password,
            required_role=RoleEnum.ADMIN,
        )
        if not token:
            return False
        request.session.update({"token": token.decode()})
        return True

    async def logout(self: Self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self: Self, request: Request) -> Response | bool:
        request_container: AsyncContainer = request.state.dishka_container
        authenticate_use_case = await request_container.get(AbstractAuthenticateUseCase)
        token = request.session.get("token")
        request.session.clear()
        if token is None or not isinstance(token, str):
            logger.warning(event="No auth token or token is not str", token=token)
            return False
        new_token = await authenticate_use_case.execute(
            token=token,
            required_role=RoleEnum.ADMIN,
        )
        if not new_token:
            return False
        request.session.update({"token": new_token.decode()})
        return True
