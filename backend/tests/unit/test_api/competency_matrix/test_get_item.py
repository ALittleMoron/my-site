import pytest_asyncio
from httpx import codes

from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.enums import PublishStatusEnum
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestGetItemAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_competency_matrix_use_case()

    def test_get_competency_matrix_item_not_found(self) -> None:
        self.use_case.get_item.side_effect = CompetencyMatrixItemNotFoundError()
        response = self.api.get_competency_matrix_item(pk=-100)
        assert response.status_code == codes.NOT_FOUND
        assert response.json() == {
            "code": "client_error",
            "type": "not_found",
            "message": "Competency matrix item not found",
            "attr": None,
            "location": None,
        }

    def test_get_competency_matrix_item_requires_only_published(self) -> None:
        response = self.api.get_competency_matrix_item(pk=1, only_published=None)
        assert response.status_code == codes.BAD_REQUEST
        self.use_case.get_item.assert_not_called()

    def test_get_competency_matrix_item(self) -> None:
        self.use_case.get_item.return_value = self.factory.core.competency_matrix_item(
            item_id=1,
            question="Как написать свою функцию?",
            publish_status=PublishStatusEnum.PUBLISHED,
            answer="Просто берёшь и пишешь!",
            interview_expected_answer="Пиши!",
            grade=GradeEnum.JUNIOR,
            subsection="Функции",
            section="Основы",
            sheet="Python",
            resources=[
                self.factory.core.attached_external_resource(
                    resource_id=1,
                    name="resource",
                    url="http://example.com",
                    context="resource context",
                ),
            ],
        )
        response = self.api.get_competency_matrix_item(pk=1)
        assert response.status_code == codes.OK
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
                },
            ],
        }
        self.use_case.get_item.assert_called_once_with(item_id=1, only_published=True)
