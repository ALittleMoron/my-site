from typing import TYPE_CHECKING, Self

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import Response
from verbose_http_exceptions import UnauthorizedHTTPException

from config.loggers import logger
from core.auth.exceptions import UserNotFoundError
from core.auth.password_hashers import PasswordHasher
from core.auth.schemas import AuthTokenPayload
from core.auth.token_handlers import TokenHandler
from db.storages.auth import AuthStorage

if TYPE_CHECKING:
    from dishka import AsyncContainer


class AdminAuthenticationBackend(AuthenticationBackend):
    async def login(self: Self, request: Request) -> bool:
        request_container: AsyncContainer = request.state.dishka_container
        storage = await request_container.get(AuthStorage)
        auth_handler = await request_container.get(TokenHandler)
        hasher = await request_container.get(PasswordHasher)
        form = await request.form()
        username, password = form["username"], form["password"]
        if not isinstance(username, str) or not isinstance(password, str):
            logger.warning(
                "username or password is not str",
                username=username,
                password=password,
            )
            return False
        try:
            user = await storage.get_user_by_username(username=username)
        except UserNotFoundError:
            logger.warning(event="No user in db from username form field", username=username)
            return False
        if not user.is_admin:
            logger.warning("User is not admin", username=user.username)
            return False
        if not hasher.verify_password(
            plain_password=password,
            hashed_password=user.password_hash.get_secret_value(),
        ):
            logger.warning(
                "incorrect credentials (passwords not suit)",
                username=user.username,
            )
            return False
        token = auth_handler.encode_token(
            payload=AuthTokenPayload(username=user.username, role=user.role),
        )
        request.session.update({"token": token.decode()})
        return True

    async def logout(self: Self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self: Self, request: Request) -> Response | bool:
        request_container: AsyncContainer = request.state.dishka_container
        storage = await request_container.get(AuthStorage)
        auth_handler = await request_container.get(TokenHandler)
        if (token := request.session.get("token")) is None or not isinstance(token, str):
            logger.warning(event="No auth token or token is not str", token=token)
            return False
        try:
            payload = auth_handler.decode_token(token.encode())
        except UnauthorizedHTTPException:
            request.session.clear()
            return False
        try:
            user = await storage.get_user_by_username(username=payload.username)
        except UserNotFoundError:
            logger.warning(event="No user in db from token payload", payload=payload)
            return False
        if not user.is_admin:
            logger.warning("User is not admin", username=user.username)
            return False
        new_token = auth_handler.encode_token(
            payload=AuthTokenPayload(username=user.username, role=user.role),
        )
        request.session.update({"token": new_token.decode()})
        return True
