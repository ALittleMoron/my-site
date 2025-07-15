from collections.abc import Iterable

from dishka import Provider

from ioc.prodivers.auth_provider import AuthProvider
from ioc.prodivers.competency_matrix_provider import CompetencyMatrixProvider
from ioc.prodivers.contacts_provider import ContactsProvider
from ioc.prodivers.database_provider import DatabaseProvider
from ioc.prodivers.general_provider import GeneralProvider
from ioc.prodivers.minio_provider import MinioProvider


def get_providers() -> Iterable[Provider]:
    return (
        GeneralProvider(),
        MinioProvider(),
        DatabaseProvider(),
        CompetencyMatrixProvider(),
        AuthProvider(),
        ContactsProvider(),
    )
