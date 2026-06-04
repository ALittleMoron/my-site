from unittest.mock import Mock

from dishka import Provider, Scope, provide

from core.wiki_links.use_cases import AbstractWikiLinksUseCase


class MockWikiLinksProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_wiki_links_use_case(self) -> AbstractWikiLinksUseCase:
        return Mock(spec=AbstractWikiLinksUseCase)
