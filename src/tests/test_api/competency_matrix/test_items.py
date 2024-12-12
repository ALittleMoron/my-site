import pytest
from litestar.di import Provide

from app.api.competency_matrix.deps import build_competency_matrix_list_items_params
from app.api.competency_matrix.endpoints import list_competency_matrix_items_handler
from app.core.competency_matrix.schemas import ListCompetencyMatrixItemsParams
from tests.fixtures import FactoryFixture
from tests.mocks.use_cases.list_competency_matrix_items import MockListCompetencyMatrixItemsUseCase
from tests.utils import create_mocked_test_client, provide_async


class TestCompetencyMatrixItemsAPI(FactoryFixture):
    use_case: MockListCompetencyMatrixItemsUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.use_case = MockListCompetencyMatrixItemsUseCase()
        self.client = create_mocked_test_client(
            handler=list_competency_matrix_items_handler,
            dependencies={
                'list_competency_matrix_items_params': Provide(
                    build_competency_matrix_list_items_params,
                ),
                'list_competency_matrix_items_use_case': provide_async(self.use_case),
            },
        )
        self.url = "/items/"

    def test_list_by_sheet_id(self) -> None:
        response = self.client.get(self.url, params={"sheetId": 1})
        assert response.is_success
        assert self.use_case.params == ListCompetencyMatrixItemsParams(sheet_id=1)

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
        response = self.client.get(self.url)
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
