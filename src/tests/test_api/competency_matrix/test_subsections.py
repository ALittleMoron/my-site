import pytest
from litestar.di import Provide

from app.api.competency_matrix.deps import build_competency_matrix_subsections_params
from app.api.competency_matrix.endpoints import list_competency_matrix_subsection_handler
from app.core.competency_matrix.schemas import ListSubsectionsParams
from tests.fixtures import FactoryFixture
from tests.mocks.use_cases.list_competency_matrix_subsections import (
    MockListSubsectionsUseCase,
)
from tests.utils import create_mocked_test_client, provide_async


class TestCompetencyMatrixSubsectionsAPI(FactoryFixture):
    use_case: MockListSubsectionsUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.use_case = MockListSubsectionsUseCase()
        self.client = create_mocked_test_client(
            handler=list_competency_matrix_subsection_handler,
            dependencies={
                'list_competency_matrix_subsections_params': Provide(
                    build_competency_matrix_subsections_params,
                ),
                'list_competency_matrix_subsections_use_case': provide_async(self.use_case),
            },
        )
        self.url = "/subsections/"

    def test_list_by_sheet_id(self) -> None:
        response = self.client.get(self.url, params={"sheetId": 1})
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
        response = self.client.get(self.url)
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
