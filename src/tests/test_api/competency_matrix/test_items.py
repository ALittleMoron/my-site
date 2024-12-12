import pytest

from app.core.competency_matrix.schemas import ListItemsParams
from tests.fixtures import ApiFixture, FactoryFixture
from tests.mocks.use_cases.list_competency_matrix_items import MockListCompetencyMatrixItemsUseCase


class TestCompetencyMatrixItemsAPI(ApiFixture, FactoryFixture):
    use_case: MockListCompetencyMatrixItemsUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.use_case = MockListCompetencyMatrixItemsUseCase()
        self.client = self.app.create_list_competency_matrix_items_client(self.use_case)

    def test_list_by_sheet_id(self) -> None:
        response = self.client.get('', params={"sheetId": 1})
        assert response.is_success
        assert self.use_case.params == ListItemsParams(sheet_id=1)

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
        response = self.client.get('')
        assert response.is_success
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
