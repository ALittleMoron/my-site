import pytest

from app.api.competency_matrix.endpoints import list_competency_matrix_sheet_handler
from tests.fixtures import FactoryFixture
from tests.mocks.use_cases.list_competency_matrix_sheets import (
    MockListSheetsUseCase,
)
from tests.utils import create_mocked_test_client, provide_async


class TestCompetencyMatrixSheetsAPI(FactoryFixture):
    use_case: MockListSheetsUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.use_case = MockListSheetsUseCase()
        self.client = create_mocked_test_client(
            handler=list_competency_matrix_sheet_handler,
            dependencies={'list_competency_matrix_sheets_use_case': provide_async(self.use_case)},
        )
        self.url = '/sheets/'

    def test_list(self) -> None:
        self.use_case.sheets = [
            self.factory.sheet(sheet_id=1, name="Python"),
            self.factory.sheet(sheet_id=2, name="JavaScript"),
        ]
        response = self.client.get(self.url)
        assert response.is_success
        assert response.json() == {
            'sheets': [
                {
                    "id": 1,
                    "name": "Python",
                },
                {
                    "id": 2,
                    "name": "JavaScript",
                },
            ],
        }
