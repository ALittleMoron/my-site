from typing import Self

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import Response
from verbose_http_exceptions import UnauthorizedHTTPException

from config.loggers import logger
from core.auth.exceptions import UserNotFoundError
from core.auth.schemas import User
from core.auth.utils import Hasher
from db.storages.auth import AuthStorage
from entrypoints.auth.handlers import AuthHandler
from entrypoints.auth.schemas import Payload
from ioc.container import container


class BaseAuthBackend(AuthenticationBackend):
    def check_permission(self, user: User) -> bool:
        raise NotImplementedError()

    async def login(self: Self, request: Request) -> bool:
        async with container() as request_container:
            storage = await request_container.get(AuthStorage)
            auth_handler = await request_container.get(AuthHandler)
            hasher = await request_container.get(Hasher)
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
            if not self.check_permission(user) or not hasher.verify_password(
                plain_password=password,
                hashed_password=user.password.get_secret_value(),
            ):
                logger.warning(
                    "incorrect credentials or user not pass permission check",
                    username=user.username,
                    permission_passed=self.check_permission(user),
                )
                return False
            token = auth_handler.encode_token(
                payload=Payload(
                    username=user.username,
                    role=user.role,
                ),
            )
            request.session.update({"token": token.decode()})
            return True

    async def logout(self: Self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self: Self, request: Request) -> Response | bool:
        async with container() as request_container:
            storage = await request_container.get(AuthStorage)
            auth_handler = await request_container.get(AuthHandler)
            if (token := request.session.get("token")) is None or not isinstance(token, str):
                logger.warning(event="No auth token or token is not str", token=token)
                return False
            try:
                payload = auth_handler.decode_token(token.encode())
            except UnauthorizedHTTPException:
                request.session.clear()
                return False
            try:
                await storage.get_user_by_username(username=payload.username)
            except UserNotFoundError:
                logger.warning(event="No user in db from token payload", payload=payload)
                return False
            return True


class AdminAuthBackend(BaseAuthBackend):
    def check_permission(self, user: User) -> bool:
        return user.is_admin


class UserAuthBackend(BaseAuthBackend):
    def check_permission(self, user: User) -> bool:
        return user.is_user


class MockAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        request.session.update({"token": "..."})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        return True
