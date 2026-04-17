from core.auth.exceptions import UnauthorizedError
from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler


def admin_user_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    if not connection.user.is_admin:
        raise UnauthorizedError
