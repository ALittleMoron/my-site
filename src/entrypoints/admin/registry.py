from collections.abc import Iterable

from sqladmin import BaseView

from entrypoints.admin.views.auth import UserView
from entrypoints.admin.views.competency_matrix import CompetencyMatrixItemView, ExternalResourceView


def get_admin_views() -> Iterable[type[BaseView]]:
    return (
        UserView,
        CompetencyMatrixItemView,
        ExternalResourceView,
    )
