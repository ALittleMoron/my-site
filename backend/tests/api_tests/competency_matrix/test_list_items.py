import pytest_asyncio
from verbose_http_exceptions import status

from core.competency_matrix.enums import StatusEnum
from tests.fixtures import ApiFixture, FactoryFixture


class TestItemsAPI(ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.app.get_mock_list_items_use_case()

    def test_list_not_correct_sheet_name(self) -> None:
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
            self.factory.competency_matrix_item(
                item_id=2,
                question="Как написать свою функцию?",
                status=StatusEnum.PUBLISHED,
                grade="Junior",
                subsection="Функции",
                section="Основы",
                sheet="JavaScript",
            ),
        ]
        response = self.api.get_competency_matrix_items(sheet_name="Java")
        assert response.status_code == status.HTTP_200_OK, response.content
        assert response.json() == {
            "sheet": "Java",
            "sections": [],
        }

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
