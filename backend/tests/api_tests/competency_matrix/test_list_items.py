from collections.abc import Generator

import pytest
from verbose_http_exceptions import status

from core.competency_matrix.enums import StatusEnum
from tests.fixtures import ApiFixture, FactoryFixture
from tests.mocks.competency_matrix.use_cases import MockListItemsUseCase


class TestItemsAPI(ApiFixture, FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> Generator[None, None, None]:
        self.use_case = MockListItemsUseCase()
        yield from self.app.override_list_competency_matrix_items(use_case=self.use_case)

    def test_list(self) -> None:
        self.use_case.items = [
            self.factory.competency_matrix_item(
                item_id=1,
                question="Как написать свою функцию?",
                status=StatusEnum.PUBLISHED,
                grade="Junior",
                subsection="Функции",
                section="Основы",
                sheet="Python",
            ),
        ]
        response = self.api.get_competency_matrix_items(sheet_name="Python")
        assert response.status_code == status.HTTP_200_OK, response.content
        assert response.json() == {
            "sheet": "Python",
            "sections": [
                {
                    "section": "Основы",
                    "subsections": [
                        {
                            "subsection": "Функции",
                            "grades": [
                                {
                                    "grade": "Junior",
                                    "items": [{"id": 1, "question": "Как написать свою функцию?"}],
                                },
                            ],
                        },
                    ],
                },
            ],
        }
