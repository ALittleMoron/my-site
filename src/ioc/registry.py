from collections.abc import Iterable

from dishka import Provider
from dishka.integrations.litestar import LitestarProvider

from ioc.prodivers.auth_provider import AuthProvider
from ioc.prodivers.blog_provider import BlogProvider
from ioc.prodivers.competency_matrix_provider import CompetencyMatrixProvider
from ioc.prodivers.contacts_provider import ContactsProvider
from ioc.prodivers.database_provider import DatabaseProvider
from ioc.prodivers.general_provider import GeneralProvider
from ioc.prodivers.markdown_provider import MarkdownProvider
from ioc.prodivers.minio_provider import MinioProvider


def get_providers() -> Iterable[Provider]:
    return (
        GeneralProvider(),
        MinioProvider(),
        DatabaseProvider(),
        LitestarProvider(),
        MarkdownProvider(),
        CompetencyMatrixProvider(),
        AuthProvider(),
        ContactsProvider(),
        BlogProvider(),
    )
