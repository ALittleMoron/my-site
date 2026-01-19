import pytest_asyncio
from httpx import codes

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.enums import PublishStatusEnum
from tests.fixtures import ApiFixture, FactoryFixture, ContainerFixture


class TestSetPublishedStatusToItemAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_publish_switch_item_use_case()

    def test_set_published_status_to_competency_matrix_item_not_found(self) -> None:
        self.use_case.execute.side_effect = CompetencyMatrixItemNotFoundError()
        response = self.api.post_set_published_status_to_item(pk=-100)
        assert response.status_code == codes.NOT_FOUND, response.content
        assert response.json() == {
            "code": "client_error",
            "type": "not_found",
            "message": "Competency matrix item not found",
            "attr": None,
            "location": None,
        }

    def test_set_published_status_to_competency_matrix_item(self) -> None:
        response = self.api.post_set_published_status_to_item(pk=1)
        assert response.status_code == codes.NO_CONTENT, response.content
        self.use_case.execute.assert_called_once_with(
            item_id=self.factory.core.int_id(1),
            publish_status=PublishStatusEnum.PUBLISHED,
        )
