from typing import ClassVar

from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler

from core.auth.exceptions import ForbiddenError, UnauthorizedError


class AdminUserGuard:
    def __call__(self, connection: ASGIConnection, _: BaseRouteHandler) -> None:
        if not connection.user.is_admin:
            raise UnauthorizedError


class DeletedTagsAccessGuard:
    true_query_values: ClassVar[frozenset[str]] = frozenset({"1", "true", "yes", "on"})

    def __call__(self, connection: ASGIConnection, _: BaseRouteHandler) -> None:
        include_deleted = str(connection.query_params.get("includeDeleted", "false")).lower()
        if include_deleted in self.true_query_values and not connection.user.is_admin:
            raise ForbiddenError


class DraftContentAccessGuard:
    false_query_values: ClassVar[frozenset[str]] = frozenset({"0", "false", "no", "off"})

    def __call__(self, connection: ASGIConnection, _: BaseRouteHandler) -> None:
        only_published = connection.query_params.get("onlyPublished")
        if only_published is None:
            return
        if str(only_published).lower() in self.false_query_values and not connection.user.is_admin:
            raise ForbiddenError


admin_user_guard = AdminUserGuard()
deleted_tags_access_guard = DeletedTagsAccessGuard()
draft_content_access_guard = DraftContentAccessGuard()
