from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, get, status_codes
from litestar.params import QueryParameter

from core.i18n.enums import LanguageEnum
from core.wiki_links.use_cases import AbstractWikiLinksUseCase
from entrypoints.litestar.api.wiki_links.schemas import WikiLinkTargetsResponseSchema
from entrypoints.litestar.guards import content_manager_guard


class WikiLinksApiController(Controller):
    path = "/wiki-links"
    tags = ["admin wiki links"]
    guards = [content_manager_guard]

    @get(
        "/targets",
        description="Получение доступных целей для typed wiki-links.",
        name="admin-wiki-links-targets-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_wiki_link_targets(
        self,
        use_case: FromDishka[AbstractWikiLinksUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> WikiLinkTargetsResponseSchema:
        targets = await use_case.list_targets(language=language)
        return WikiLinkTargetsResponseSchema.from_domain_schema(schema=targets)


admin_router = DishkaRouter("", route_handlers=[WikiLinksApiController])
