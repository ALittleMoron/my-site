import pytest

from tests.fixtures import ApiFixture, FactoryFixture
from tests.mocks.use_cases.list_competency_matrix_sheets import (
    MockListSheetsUseCase,
)


class TestCompetencyMatrixSheetsAPI(ApiFixture, FactoryFixture):
    use_case: MockListSheetsUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.use_case = MockListSheetsUseCase()
        self.client = self.app.create_list_competency_matrix_sheets_client(self.use_case)

    def test_list(self) -> None:
        self.use_case.sheets = [
            self.factory.sheet(sheet_id=1, name="Python"),
            self.factory.sheet(sheet_id=2, name="JavaScript"),
        ]
        response = self.client.get('')
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
