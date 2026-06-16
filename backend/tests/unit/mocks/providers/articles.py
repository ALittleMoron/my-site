from unittest.mock import Mock

from dishka import Provider, Scope, provide

from core.articles.schemas import ArticlePublicStatsCollection
from core.articles.use_cases import AbstractArticleAnalyticsUseCase, AbstractArticlesUseCase


class MockArticlesProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_articles_use_case(self) -> AbstractArticlesUseCase:
        return Mock(spec=AbstractArticlesUseCase)

    @provide(scope=Scope.APP)
    async def provide_article_analytics_use_case(self) -> AbstractArticleAnalyticsUseCase:
        mock = Mock(spec=AbstractArticleAnalyticsUseCase)
        mock.get_public_stats.return_value = ArticlePublicStatsCollection(values=[])
        return mock
