from collections.abc import Iterable

from dishka import Provider
from dishka.integrations.litestar import LitestarProvider

from infra.ioc.prodivers.account_provider import UserAccountProvider
from infra.ioc.prodivers.auth_provider import AuthProvider
from infra.ioc.prodivers.competency_matrix_provider import CompetencyMatrixProvider
from infra.ioc.prodivers.contacts_provider import ContactsProvider
from infra.ioc.prodivers.database_provider import DatabaseProvider
from infra.ioc.prodivers.files_provider import FilesProvider
from infra.ioc.prodivers.general_provider import GeneralProvider
from infra.ioc.prodivers.notes_provider import NotesProvider
from infra.ioc.prodivers.response_cache_warm_provider import ResponseCacheWarmProvider
from infra.ioc.prodivers.wiki_links_provider import WikiLinksProvider


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
        NotesProvider(),
        WikiLinksProvider(),
        ResponseCacheWarmProvider(),
    )
