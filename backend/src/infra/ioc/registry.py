from collections.abc import Iterable

from dishka import Provider
from dishka.integrations.litestar import LitestarProvider

from infra.ioc.prodivers.account_provider import UserAccountProvider
from infra.ioc.prodivers.auth_provider import AuthProvider
from infra.ioc.prodivers.blog_provider import BlogProvider
from infra.ioc.prodivers.competency_matrix_provider import CompetencyMatrixProvider
from infra.ioc.prodivers.contacts_provider import ContactsProvider
from infra.ioc.prodivers.database_provider import DatabaseProvider
from infra.ioc.prodivers.files_provider import FilesProvider
from infra.ioc.prodivers.general_provider import GeneralProvider


def get_providers() -> Iterable[Provider]:
    return (
        GeneralProvider(),
        FilesProvider(),
        DatabaseProvider(),
        LitestarProvider(),
        CompetencyMatrixProvider(),
        UserAccountProvider(),
        AuthProvider(),
        ContactsProvider(),
        BlogProvider(),
    )
