from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Self

from sqladmin.authentication import AuthenticationBackend
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import Response

from config.loggers import logger
from config.settings import settings
from core.auth.enums import RoleEnum
from core.auth.exceptions import UnauthorizedError
from core.auth.schemas import AuthTokenPayload
from core.auth.token_handlers import TokenHandler

if TYPE_CHECKING:
    from dishka import AsyncContainer


@dataclass(kw_only=True, slots=True, frozen=True)
class SessionConfig:
    secret_key: str
    session_cookie: str = "session"
    max_age: int | None = 14 * 24 * 60 * 60  # 14 days, in seconds
    path: str = "/"
    same_site: Literal["lax", "strict", "none"] = "lax"
    https_only: bool = False
    domain: str | None = None


class AdminAuthenticationBackend(AuthenticationBackend):
    def __init__(self, session_config: SessionConfig) -> None:
        self.middlewares = [
            Middleware(
                SessionMiddleware,
                secret_key=session_config.secret_key,
                session_cookie=session_config.session_cookie,
                max_age=session_config.max_age,
                path=session_config.path,
                same_site=session_config.same_site,
                https_only=session_config.https_only,
                domain=session_config.domain,
            ),
        ]

    async def login(self: Self, request: Request) -> bool:
        request_container: AsyncContainer = request.state.dishka_container
        token_handler = await request_container.get(TokenHandler)
        form = await request.form()
        username, password = form["username"], form["password"]
        if not isinstance(username, str) or not isinstance(password, str):
            logger.warning("username or password is not str", username=username, password=password)
            return False
        if (
            username != settings.admin.init_username
            or password != settings.admin.init_password.get_secret_value()
        ):
            logger.warning("incorrect admin credentials", username=username, password=password)
            return False
        payload = AuthTokenPayload(username=username, role=RoleEnum.ADMIN)
        token = token_handler.encode_token(payload=payload)
        request.session.update({"token": token.decode()})
        return True

    async def logout(self: Self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self: Self, request: Request) -> Response | bool:
        request_container: AsyncContainer = request.state.dishka_container
        token_handler = await request_container.get(TokenHandler)
        token = request.session.get("token")
        request.session.clear()
        if token is None or not isinstance(token, str):
            logger.warning(event="No auth token or token is not str", token=token)
            return False
        try:
            payload = token_handler.decode_token(token.encode())
        except UnauthorizedError:
            return False
        if payload.username != settings.admin.init_username or payload.role != RoleEnum.ADMIN:
            logger.warning(
                event="Token payload is invalid for admin auth backend",
                username=payload.username,
                role=payload.role,
            )
            return False
        payload = AuthTokenPayload(username=payload.username, role=RoleEnum.ADMIN)
        new_token = token_handler.encode_token(payload=payload)
        request.session.update({"token": new_token.decode()})
        return True
