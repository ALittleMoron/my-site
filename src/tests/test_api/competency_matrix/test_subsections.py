import datetime
from collections.abc import Generator

import pytest

from app.core.competency_matrix.schemas import ListSubsectionsParams
from tests.fixtures import ApiFixture, FactoryFixture
from tests.mocks.use_cases.list_competency_matrix_subsections import (
    MockListSubsectionsUseCase,
)


class TestCompetencyMatrixSubsectionsAPI(ApiFixture, FactoryFixture):
    current_datetime: datetime.datetime
    use_case: MockListSubsectionsUseCase

    @pytest.fixture(autouse=True)
    def setup(
        self,
        mock_list_competency_matrix_subsections_use_case: MockListSubsectionsUseCase,
    ) -> Generator[None, None, None]:
        self.current_datetime = datetime.datetime.now(tz=datetime.UTC)
        self.use_case = mock_list_competency_matrix_subsections_use_case
        yield
        self.use_case.items = []

    def test_list_by_sheet_id(self) -> None:
        response = self.mocked_api.list_competency_matrix_subsections(sheet_id=1)
        assert response.is_success
        assert self.use_case.params == ListSubsectionsParams(sheet_id=1)

    def test_list(self) -> None:
        self.use_case.subsections = [
            self.factory.subsection(
                subsection_id=1,
                name="Функции",
                section=self.factory.section(
                    section_id=1,
                    name="Основы",
                    sheet=self.factory.sheet(sheet_id=1, name="Python"),
                ),
            ),
            self.factory.subsection(
                subsection_id=2,
                name="Протоколы",
                section=self.factory.section(
                    section_id=2,
                    name="ООП",
                    sheet=self.factory.sheet(sheet_id=2, name="JavaScript"),
                ),
            ),
        ]
        response = self.mocked_api.list_competency_matrix_subsections()
        assert response.is_success
        assert response.json() == {
            'subsections': [
                {
                    "id": 1,
                    "name": "Функции",
                    "section": {
                        "id": 1,
                        "name": "Основы",
                        "sheet": {
                            "id": 1,
                            "name": "Python",
                        },
                    },
                },
                {
                    "id": 2,
                    "name": "Протоколы",
                    "section": {
                        "id": 2,
                        "name": "ООП",
                        "sheet": {
                            "id": 2,
                            "name": "JavaScript",
                        },
                    },
                },
            ],
        }
