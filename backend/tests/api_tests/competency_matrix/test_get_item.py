import pytest_asyncio
from verbose_http_exceptions import status

from core.competency_matrix.enums import StatusEnum
from tests.fixtures import ApiFixture, FactoryFixture


class TestGetItemAPI(ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.app.get_mock_get_item_use_case()

    def test_not_found(self) -> None:
        self.use_case.item = None
        response = self.api.get_competency_matrix_item(item_id=-100)
        assert self.use_case.item_id == -100
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "code": "client_error",
            "type": "not_found",
            "message": "Competency matrix item not found",
            "attr": None,
            "location": None,
        }

    def test_found(self) -> None:
        self.use_case.item = self.factory.competency_matrix_item(
            item_id=1,
            question="Как написать свою функцию?",
            status=StatusEnum.PUBLISHED,
            answer="Просто берёшь и пишешь!",
            interview_expected_answer="Пиши!",
            grade="Junior",
            subsection="Функции",
            section="Основы",
            sheet="Python",
            resources=[
                self.factory.resource(
                    resource_id=1,
                    name="resource",
                    url="http://example.com",
                    context="resource context",
                ),
            ],
        )
        response = self.api.get_competency_matrix_item(item_id=1)
        assert self.use_case.item_id == 1
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
            "resources": [
                {
                    "id": 1,
                    "name": "resource",
                    "url": "http://example.com",
                    "context": "resource context",
                }
            ],
        }
