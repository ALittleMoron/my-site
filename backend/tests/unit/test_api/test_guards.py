from typing import Any, cast
from unittest.mock import Mock

import pytest
from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler

from core.auth.enums import RoleEnum
from core.auth.exceptions import ForbiddenError, UnauthorizedError
from core.auth.schemas import JwtUser
from entrypoints.litestar.guards import (
    admin_user_guard,
    content_manager_guard,
    deleted_tags_access_guard,
    draft_content_access_guard,
)


class FakeConnection:
    def __init__(self, user: JwtUser, query_params: dict[str, str] | None = None) -> None:
        self.user = user
        self.query_params = query_params or {}


def make_connection(
    user: JwtUser,
    query_params: dict[str, str] | None = None,
) -> ASGIConnection[Any, Any, Any, Any]:
    return cast("ASGIConnection[Any, Any, Any, Any]", FakeConnection(user, query_params))


def make_route_handler() -> BaseRouteHandler:
    return cast("BaseRouteHandler", Mock())


class TestGuards:
    def test_admin_guard_allows_only_exact_admin(self) -> None:
        admin_connection = make_connection(JwtUser(username="admin", role=RoleEnum.ADMIN))
        moderator_connection = make_connection(
            JwtUser(username="moderator", role=RoleEnum.MODERATOR),
        )

        admin_user_guard(admin_connection, make_route_handler())
        with pytest.raises(UnauthorizedError):
            admin_user_guard(moderator_connection, make_route_handler())

    @pytest.mark.parametrize("role", [RoleEnum.ADMIN, RoleEnum.MODERATOR])
    def test_content_manager_guard_allows_content_roles(self, role: RoleEnum) -> None:
        connection = make_connection(JwtUser(username=role.value, role=role))

        content_manager_guard(connection, make_route_handler())

    def test_content_manager_guard_rejects_regular_user(self) -> None:
        connection = make_connection(JwtUser(username="user", role=RoleEnum.USER))

        with pytest.raises(UnauthorizedError):
            content_manager_guard(connection, make_route_handler())

    @pytest.mark.parametrize("role", [RoleEnum.ADMIN, RoleEnum.MODERATOR])
    def test_draft_content_guard_allows_content_roles_to_request_all_content(
        self,
        role: RoleEnum,
    ) -> None:
        connection = make_connection(
            JwtUser(username=role.value, role=role),
            query_params={"onlyPublished": "false"},
        )

        draft_content_access_guard(connection, make_route_handler())

    def test_draft_content_guard_rejects_regular_user_requesting_all_content(self) -> None:
        connection = make_connection(
            JwtUser(username="user", role=RoleEnum.USER),
            query_params={"onlyPublished": "false"},
        )

        with pytest.raises(ForbiddenError):
            draft_content_access_guard(connection, make_route_handler())

    @pytest.mark.parametrize("role", [RoleEnum.ADMIN, RoleEnum.MODERATOR])
    def test_deleted_tags_guard_allows_content_roles_to_include_deleted_tags(
        self,
        role: RoleEnum,
    ) -> None:
        connection = make_connection(
            JwtUser(username=role.value, role=role),
            query_params={"includeDeleted": "true"},
        )

        deleted_tags_access_guard(connection, make_route_handler())

    def test_deleted_tags_guard_rejects_regular_user_include_deleted_tags(self) -> None:
        connection = make_connection(
            JwtUser(username="user", role=RoleEnum.USER),
            query_params={"includeDeleted": "true"},
        )

        with pytest.raises(ForbiddenError):
            deleted_tags_access_guard(connection, make_route_handler())
