from collections.abc import Generator

import pytest
from verbose_http_exceptions import status

from tests.fixtures import ApiFixture
from tests.mocks.competency_matrix.use_cases import MockListSheetsUseCase


class TestSheetsAPI(ApiFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> Generator[None, None, None]:
        self.use_case = MockListSheetsUseCase()
        yield from self.app.override_list_sheets_use_case(use_case=self.use_case)

    def test_list(self) -> None:
        self.use_case.sheets = ["Python", "SQL"]
        response = self.api.get_competency_matrix_sheets()
        assert response.status_code == status.HTTP_200_OK, response.content
        assert response.json() == {"sheets": ["Python", "SQL"]}
