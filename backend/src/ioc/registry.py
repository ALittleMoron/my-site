from collections.abc import Iterable

from dishka import Provider

from ioc.prodivers.auth_provider import AuthProvider
from ioc.prodivers.competency_matrix_provider import CompetencyMatrixProvider
from ioc.prodivers.database_provider import DatabaseProvider


def get_providers() -> Iterable[Provider]:
    return (
        DatabaseProvider(),
        CompetencyMatrixProvider(),
        AuthProvider(),
    )
