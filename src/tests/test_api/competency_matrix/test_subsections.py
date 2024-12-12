import pytest

from app.core.competency_matrix.schemas import ListSubsectionsParams
from tests.fixtures import FactoryFixture, ApiFixture
from tests.mocks.use_cases.list_competency_matrix_subsections import (
    MockListSubsectionsUseCase,
)


class TestCompetencyMatrixSubsectionsAPI(ApiFixture, FactoryFixture):
    use_case: MockListSubsectionsUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.use_case = MockListSubsectionsUseCase()
        self.client = self.app.create_list_competency_matrix_subsections_client(self.use_case)

    def test_list_by_sheet_id(self) -> None:
        response = self.client.get('', params={"sheetId": 1})
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
        response = self.client.get('')
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
