from unittest.mock import Mock

from dishka import Provider, Scope, provide

from core.agent_access.use_cases import AgentAdminUseCase


class MockAgentAccessProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_agent_admin_use_case(self) -> AgentAdminUseCase:
        return Mock(spec=AgentAdminUseCase)
