from dishka import Provider, Scope, provide

from core.markdown.services import MarkdownService
from services.markdown import MarkdownItService


class MarkdownProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_markdown_service(self) -> MarkdownService:
        return MarkdownItService()
