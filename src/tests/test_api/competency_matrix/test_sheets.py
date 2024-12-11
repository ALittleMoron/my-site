import datetime
from collections.abc import Generator

import pytest

from tests.fixtures import ApiFixture, FactoryFixture
from tests.mocks.use_cases.list_competency_matrix_sheets import (
    MockListCompetencyMatrixSheetsUseCase,
)


class TestCompetencyMatrixSheetsAPI(ApiFixture, FactoryFixture):
    current_datetime: datetime.datetime
    use_case: MockListCompetencyMatrixSheetsUseCase

    @pytest.fixture(autouse=True)
    def setup(
        self,
        mock_list_competency_matrix_sheets_use_case: MockListCompetencyMatrixSheetsUseCase,
    ) -> Generator[None, None, None]:
        self.current_datetime = datetime.datetime.now(tz=datetime.UTC)
        self.use_case = mock_list_competency_matrix_sheets_use_case
        yield
        self.use_case.items = []

    def test_list(self) -> None:
        self.use_case.sheets = [
            self.factory.sheet(sheet_id=1, name="Python"),
            self.factory.sheet(sheet_id=2, name="JavaScript"),
        ]
        response = self.mocked_api.list_competency_matrix_sheets()
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
            ]
        }
