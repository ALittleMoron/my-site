from dishka import Provider, Scope, alias, provide

from core.agent_access.clients import AgentCertificateIssuer
from core.agent_access.schemas import AgentCertificatePolicy, MatrixAgentPolicy
from core.agent_access.storages import (
    AgentAdminStorage,
    AgentAuditStorage,
    AgentCertificateRotationStorage,
    AgentIdentityStorage,
    MatrixAgentStorage,
)
from core.agent_access.use_cases import (
    AgentAuditUseCase,
    AgentCertificateRotationUseCase,
    AgentIdentityUseCase,
    MatrixAgentUseCase,
)
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.generators import HexUuidIdGenerator
from infra.postgresql.storages.agent_access import AgentAccessDatabaseStorage


class AgentAccessProvider(Provider):
    def __init__(
        self,
        *,
        certificate_policy: AgentCertificatePolicy,
        matrix_policy: MatrixAgentPolicy,
    ) -> None:
        super().__init__()
        self.certificate_policy = certificate_policy
        self.matrix_policy = matrix_policy

    agent_access_database_storage = provide(AgentAccessDatabaseStorage, scope=Scope.REQUEST)
    agent_admin_storage = alias(AgentAccessDatabaseStorage, provides=AgentAdminStorage)
    agent_audit_storage = alias(AgentAccessDatabaseStorage, provides=AgentAuditStorage)
    agent_identity_storage = alias(AgentAccessDatabaseStorage, provides=AgentIdentityStorage)
    agent_certificate_rotation_storage = alias(
        AgentAccessDatabaseStorage,
        provides=AgentCertificateRotationStorage,
    )
    matrix_agent_storage = alias(AgentAccessDatabaseStorage, provides=MatrixAgentStorage)
    agent_identity_use_case = provide(AgentIdentityUseCase, scope=Scope.REQUEST)
    agent_audit_use_case = provide(AgentAuditUseCase, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    def provide_agent_certificate_rotation_use_case(
        self,
        storage: AgentCertificateRotationStorage,
        certificate_issuer: AgentCertificateIssuer,
        id_generator: HexUuidIdGenerator,
    ) -> AgentCertificateRotationUseCase:
        return AgentCertificateRotationUseCase(
            storage=storage,
            certificate_issuer=certificate_issuer,
            id_generator=id_generator,
            policy=self.certificate_policy,
        )

    @provide(scope=Scope.REQUEST)
    def provide_matrix_agent_use_case(
        self,
        storage: MatrixAgentStorage,
        matrix_storage: CompetencyMatrixStorage,
        id_generator: HexUuidIdGenerator,
    ) -> MatrixAgentUseCase:
        return MatrixAgentUseCase(
            storage=storage,
            matrix_storage=matrix_storage,
            id_generator=id_generator,
            policy=self.matrix_policy,
        )
