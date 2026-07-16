from collections.abc import Iterable

from dishka import Provider
from dishka.integrations.litestar import LitestarProvider

from core.agent_access.schemas import AgentAuditPolicy, AgentCertificatePolicy, MatrixAgentPolicy
from infra.config.constants import constants
from infra.config.settings import settings
from infra.ioc.prodivers.account_provider import UserAccountProvider
from infra.ioc.prodivers.agent_access_provider import AgentAccessProvider
from infra.ioc.prodivers.agent_admin_provider import AgentAdminProvider
from infra.ioc.prodivers.articles_provider import ArticlesProvider
from infra.ioc.prodivers.auth_provider import AuthProvider
from infra.ioc.prodivers.competency_matrix_provider import CompetencyMatrixProvider
from infra.ioc.prodivers.contacts_provider import ContactsProvider
from infra.ioc.prodivers.database_provider import DatabaseProvider
from infra.ioc.prodivers.files_provider import FilesProvider
from infra.ioc.prodivers.general_provider import GeneralProvider
from infra.ioc.prodivers.healthcheck_provider import HealthcheckProvider
from infra.ioc.prodivers.response_cache_warm_provider import ResponseCacheWarmProvider
from infra.ioc.prodivers.resumes_provider import ResumesProvider
from infra.ioc.prodivers.wiki_links_provider import WikiLinksProvider


def get_providers() -> Iterable[Provider]:
    certificate_policy = AgentCertificatePolicy(
        lifetime_seconds=constants.agent_access.certificate_lifetime_seconds,
        rotation_window_seconds=constants.agent_access.certificate_rotation_window_seconds,
        normal_access_overlap_seconds=(
            constants.agent_access.certificate_rotation_normal_access_overlap_seconds
        ),
    )
    audit_policy = AgentAuditPolicy(
        page_size_max=constants.agent_access.audit_page_max_size,
        retention_seconds=constants.agent_access.audit_retention_seconds,
    )
    matrix_policy = MatrixAgentPolicy(
        claim_ttl_seconds=constants.agent_access.claim_ttl_seconds,
        minimum_resource_count=constants.agent_access.minimum_resource_count,
        maximum_resource_count=constants.agent_access.maximum_resource_count,
    )
    return (
        GeneralProvider(),
        FilesProvider(),
        DatabaseProvider(),
        AgentAdminProvider(
            settings=settings.agent_access,
            certificate_policy=certificate_policy,
            audit_policy=audit_policy,
        ),
        AgentAccessProvider(
            certificate_policy=certificate_policy,
            matrix_policy=matrix_policy,
        ),
        LitestarProvider(),
        CompetencyMatrixProvider(),
        UserAccountProvider(),
        AuthProvider(),
        ContactsProvider(),
        ArticlesProvider(),
        ResumesProvider(),
        WikiLinksProvider(),
        ResponseCacheWarmProvider(),
        HealthcheckProvider(),
    )
