import pytest_asyncio
from httpx import codes

from core.i18n.enums import LanguageEnum
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestFindResourcesAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_competency_matrix_use_case()

    def test_search_resources(self) -> None:
        self.use_case.find_resources.return_value = self.factory.core.external_resources(
            values=[
                self.factory.core.external_resource(
                    resource_id=1,
                    name_ru="документация",
                    name_en="documentation",
                    url="https://example.com",
                ),
            ],
        )
        response = self.api.get_search_competency_matrix_resources(
            search_name="test",
            language="en",
        )
        assert response.status_code == codes.OK
        assert response.json() == {
            "resources": [
                {
                    "id": 1,
                    "name": "documentation",
                    "url": "https://example.com",
                    "translations": {
                        "ru": {"name": "документация"},
                        "en": {"name": "documentation"},
                    },
                },
            ],
        }
        self.use_case.find_resources.assert_called_once_with(
            search_name=self.factory.core.search_name("test"),
            limit=10,
            language=LanguageEnum.EN,
        )

    def test_search_resources_requires_limit(self) -> None:
        response = self.api.get_search_competency_matrix_resources(search_name="test", limit=None)
        assert response.status_code == codes.BAD_REQUEST
        self.use_case.find_resources.assert_not_called()

    def test_search_resources_requires_explicit_language(self) -> None:
        response = self.api.get_search_competency_matrix_resources(
            search_name="test",
            language=None,
        )
        assert response.status_code == codes.BAD_REQUEST
        self.use_case.find_resources.assert_not_called()
