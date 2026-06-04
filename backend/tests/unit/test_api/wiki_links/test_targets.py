import pytest_asyncio
from httpx import codes

from core.i18n.enums import LanguageEnum
from core.wiki_links.enums import WikiLinkTargetTypeEnum
from core.wiki_links.schemas import WikiLinkTargetGroup, WikiLinkTargets
from tests.unit.fixtures import ApiFixture, ContainerFixture


class TestWikiLinkTargetsAPI(ContainerFixture, ApiFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_wiki_links_use_case()

    def test_list_targets(self) -> None:
        self.use_case.list_targets.return_value = WikiLinkTargets(
            values=[
                WikiLinkTargetGroup(
                    type=WikiLinkTargetTypeEnum.NOTES,
                    slugs=["typed-notes"],
                ),
                WikiLinkTargetGroup(
                    type=WikiLinkTargetTypeEnum.MATRIX,
                    slugs=["how-to-write-function"],
                ),
            ],
        )

        response = self.api.get_wiki_link_targets(language="ru")

        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "targets": [
                {"type": "notes", "slugs": ["typed-notes"]},
                {"type": "matrix", "slugs": ["how-to-write-function"]},
            ],
        }
        self.use_case.list_targets.assert_called_once_with(language=LanguageEnum.RU)

    def test_requires_explicit_language(self) -> None:
        response = self.api.get_wiki_link_targets(language=None)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.list_targets.assert_not_called()

    def test_requires_admin(self) -> None:
        response = self.no_auth_api.get_wiki_link_targets(language="ru")

        assert response.status_code == codes.UNAUTHORIZED
        self.use_case.list_targets.assert_not_called()
