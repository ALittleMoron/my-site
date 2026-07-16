from unittest.mock import Mock

from dishka import Provider, Scope, provide

from core.cache_tools.use_cases import CacheToolsUseCase


class MockCacheToolsProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_cache_tools_use_case(self) -> CacheToolsUseCase:
        return Mock(spec=CacheToolsUseCase)
