from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler

from core.auth.exceptions import UnauthorizedError


class AdminUserGuard:
    def __call__(self, connection: ASGIConnection, _: BaseRouteHandler) -> None:
        if not connection.user.is_admin:
            raise UnauthorizedError


class ContentManagerGuard:
    def __call__(self, connection: ASGIConnection, _: BaseRouteHandler) -> None:
        if not connection.user.can_manage_content:
            raise UnauthorizedError


admin_user_guard = AdminUserGuard()
content_manager_guard = ContentManagerGuard()
