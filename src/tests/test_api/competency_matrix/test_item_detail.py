import datetime

import pytest
from httpx import codes

from app.core.competency_matrix.enums import StatusEnum
from app.core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from tests.fixtures import ApiFixture, FactoryFixture
from tests.mocks.use_cases.detail_competecy_matrix_item import MockGetItemUseCase


class TestCompetencyMatrixItemsAPI(ApiFixture, FactoryFixture):
    use_case: MockGetItemUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.use_case = MockGetItemUseCase()
        self.current_datetime = datetime.datetime.now(tz=datetime.UTC)
        self.client = self.app.create_detail_competency_matrix_item_client(self.use_case)

    def test_not_found(self) -> None:
        self.use_case.raise_exception = CompetencyMatrixItemNotFoundError()
        response = self.client.get('1')
        assert response.status_code == codes.NOT_FOUND

    def test_get(self) -> None:
        self.use_case.item = self.factory.full_competency_matrix_item(
            item_id=1,
            question="QUESTION",
            status=StatusEnum.PUBLISHED,
            status_changed=self.current_datetime,
            answer="ANSWER",
            interview_expected_answer="EXPECTED",
            grade_id=1,
            grade=self.factory.grade(grade_id=1, name="GRADE"),
            subsection_id=1,
            subsection=self.factory.subsection(
                subsection_id=1,
                name="SUBSECTION",
                section=self.factory.section(
                    section_id=1,
                    name="SECTION",
                    sheet=self.factory.sheet(sheet_id=1, name="SHEET"),
                ),
            ),
            resources=[
                self.factory.resource(
                    resource_id=1,
                    name="RESOURCE",
                    url="https://example.com",
                    context="CONTEXT",
                ),
            ],
        )
        response = self.client.get('1')
        assert response.status_code == codes.OK
        assert response.json() == {
            "id": 1,
            "question": "QUESTION",
            "answer": "ANSWER",
            "interviewExpectedAnswer": "EXPECTED",
            "grade": {
                "id": 1,
                "name": "GRADE",
            },
            "subsection": {
                "id": 1,
                "name": "SUBSECTION",
                "section": {
                    "id": 1,
                    "name": "SECTION",
                    "sheet": {
                        "id": 1,
                        "name": "SHEET",
                    },
                },
            },
            "resources": [
                {
                    "id": 1,
                    "name": "RESOURCE",
                    "url": "https://example.com",
                    "context": "CONTEXT",
                },
            ],
        }
