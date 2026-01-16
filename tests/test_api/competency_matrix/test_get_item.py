import pytest_asyncio
from verbose_http_exceptions import status

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.enums import PublishStatusEnum
from tests.fixtures import ApiFixture, FactoryFixture, ContainerFixture


class TestGetItemAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_get_item_use_case()

    def test_get_competency_matrix_item_not_found(self) -> None:
        self.use_case.execute.side_effect = CompetencyMatrixItemNotFoundError()
        response = self.api.get_competency_matrix_item(item_id=-100)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "code": "client_error",
            "type": "not_found",
            "message": "Competency matrix item not found",
            "attr": None,
            "location": None,
        }

    def test_get_competency_matrix_item(self) -> None:
        self.use_case.execute.return_value = self.factory.core.competency_matrix_item(
            item_id=1,
            question="Как написать свою функцию?",
            publish_status=PublishStatusEnum.PUBLISHED,
            answer="Просто берёшь и пишешь!",
            interview_expected_answer="Пиши!",
            grade="Junior",
            subsection="Функции",
            section="Основы",
            sheet="Python",
            resources=[
                self.factory.core.resource(
                    resource_id=1,
                    name="resource",
                    url="http://example.com",
                    context="resource context",
                ),
            ],
        )
        response = self.api.get_competency_matrix_item(item_id=1)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": 1,
            "question": "Как написать свою функцию?",
            "answer": "Просто берёшь и пишешь!",
            "interviewExpectedAnswer": "Пиши!",
            "grade": "Junior",
            "subsection": "Функции",
            "section": "Основы",
            "sheet": "Python",
            "publishStatus": "Published",
            "resources": [
                {
                    "id": 1,
                    "name": "resource",
                    "url": "http://example.com",
                    "context": "resource context",
                }
            ],
        }
        self.use_case.execute.assert_called_once_with(item_id=1, only_published=True)
