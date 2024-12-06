import datetime
from collections.abc import Generator

import pytest

from tests.fixtures import ApiFixture, FactoryFixture
from tests.mocks.use_cases.list_competency_matrix_items import MockListCompetencyMatrixItems


class TestCompetencyMatrixItems(ApiFixture, FactoryFixture):
    current_datetime: datetime.datetime
    use_case: MockListCompetencyMatrixItems

    @pytest.fixture(autouse=True)
    def setup(
        self,
        mock_list_competency_matrix_items_use_case: MockListCompetencyMatrixItems,
    ) -> Generator[None, None, None]:
        self.current_datetime = datetime.datetime.now(tz=datetime.UTC)
        self.use_case = mock_list_competency_matrix_items_use_case
        yield
        self.use_case.items = []

    def test_list(self) -> None:
        self.use_case.items = [
            self.factory.short_filled_competency_matrix_item(
                item_id=1,
                question="range - это итератор?",
                grade_id=1,
                subsection_id=1,
            ),
            self.factory.short_filled_competency_matrix_item(
                item_id=2,
                question="Что такое декоратор?",
                grade_id=2,
                subsection_id=2,
            ),
        ]
        response = self.api.list_competency_matrix()
        assert response.is_success, response.text
        assert response.json() == {
            'items': [
                {
                    "id": 1,
                    "question": "range - это итератор?",
                    "grade_id": 1,
                    "subsection_id": 1,
                },
                {
                    "id": 2,
                    "question": "Что такое декоратор?",
                    "grade_id": 2,
                    "subsection_id": 2,
                },
            ],
        }
