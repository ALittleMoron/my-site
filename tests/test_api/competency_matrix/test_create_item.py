from unittest.mock import ANY

import pytest_asyncio
from httpx import codes

from core.competency_matrix.enums import GradeEnum
from core.enums import PublishStatusEnum
from tests.fixtures import ContainerFixture, ApiFixture, FactoryFixture


class TestCreateItemAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_upsert_item_use_case()

    def test_create_item(self) -> None:
        self.use_case.execute.return_value = self.factory.core.competency_matrix_item(
            item_id=1,
            question="question 1",
            answer="answer 1",
            interview_expected_answer="interview expected answer 1",
            sheet="Python",
            grade=GradeEnum.JUNIOR,
            section="Section",
            subsection="Subsection",
            publish_status=PublishStatusEnum.DRAFT,
            resources=[
                self.factory.core.external_resource(
                    resource_id=1,
                    name="resource 1",
                    url="http://example.com",
                    context="resource context 1",
                )
            ],
        )
        response = self.api.post_create_item(
            data={
                "question": "question 1",
                "answer": "answer 1",
                "interviewExpectedAnswer": "interview expected answer 1",
                "sheet": "Python",
                "grade": "Junior",
                "section": "Section",
                "subsection": "Subsection",
                "publishStatus": "Draft",
                "resources": [
                    1,
                    2,
                    {
                        "name": "resource 1",
                        "url": "http://example.com",
                        "context": "resource context 1",
                    },
                ],
            }
        )
        self.use_case.execute.assert_called_once_with(
            params=self.factory.core.competency_matrix_item_upsert_params(
                item_id=1,
                question="question 1",
                answer="answer 1",
                interview_expected_answer="interview expected answer 1",
                sheet="Python",
                grade=GradeEnum.JUNIOR,
                section="Section",
                subsection="Subsection",
                publish_status=PublishStatusEnum.DRAFT,
                resources=[
                    self.factory.core.int_id(1),
                    self.factory.core.int_id(2),
                    self.factory.core.external_resource(
                        resource_id=ANY,
                        name="resource 1",
                        url="http://example.com",
                        context="resource context 1",
                    ),
                ],
            ),
        )
        assert response.status_code == codes.CREATED, response.json()
        assert response.json() == {
            "id": 1,
            "question": "question 1",
            "answer": "answer 1",
            "interviewExpectedAnswer": "interview expected answer 1",
            "sheet": "Python",
            "grade": "Junior",
            "section": "Section",
            "subsection": "Subsection",
            "publishStatus": PublishStatusEnum.DRAFT.value,
            "resources": [
                {
                    "id": ANY,
                    "name": "resource 1",
                    "url": "http://example.com",
                    "context": "resource context 1",
                },
            ],
        }
