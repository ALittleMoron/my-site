from dishka import Provider, Scope, provide

from entrypoints.litestar.response_cache import (
    ResponseCacheDomain,
    ResponseCacheDomainStore,
)
from entrypoints.taskiq.cache_warm.service import ResponseCacheWarmService
from entrypoints.taskiq.cache_warm.targets import (
    ArticlesCacheWarmTargetCollector,
    CacheWarmQueryBuilder,
    CompetencyMatrixCacheWarmTargetCollector,
    I18nCacheWarmTargetCollector,
    ResponseCacheWarmTargetCollector,
)
from entrypoints.taskiq.cache_warm.writer import ResponseCacheWarmWriter
from infra.config.settings import settings


class ResponseCacheWarmProvider(Provider):
    scope = Scope.REQUEST

    cache_warm_query_builder = provide(CacheWarmQueryBuilder)
    i18n_cache_warm_target_collector = provide(I18nCacheWarmTargetCollector)
    articles_cache_warm_target_collector = provide(ArticlesCacheWarmTargetCollector)
    competency_matrix_cache_warm_target_collector = provide(
        CompetencyMatrixCacheWarmTargetCollector,
    )
    response_cache_warm_target_collector = provide(ResponseCacheWarmTargetCollector)
    response_cache_warm_writer = provide(ResponseCacheWarmWriter)

    @provide
    async def provide_response_cache_domain_store(self) -> ResponseCacheDomainStore:
        from entrypoints.litestar.initializers import (  # noqa: PLC0415
            create_response_cache_domain_store,
        )

        return create_response_cache_domain_store()

    @provide
    async def provide_response_cache_warm_service(
        self,
        target_collector: ResponseCacheWarmTargetCollector,
        writer: ResponseCacheWarmWriter,
    ) -> ResponseCacheWarmService:
        return ResponseCacheWarmService(
            target_collector=target_collector,
            writer=writer,
            use_cache=settings.app.use_cache,
            supported_domains=(
                ResponseCacheDomain.I18N,
                ResponseCacheDomain.ARTICLES,
                ResponseCacheDomain.COMPETENCY_MATRIX,
            ),
        )
