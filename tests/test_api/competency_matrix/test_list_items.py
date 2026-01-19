import pytest_asyncio
from httpx import codes

from core.enums import PublishStatusEnum
from tests.fixtures import ApiFixture, FactoryFixture, ContainerFixture


class TestItemsAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_list_items_use_case()

    def test_list_not_correct_sheet_name(self) -> None:
        self.use_case.execute.return_value = self.factory.core.competency_matrix_items(
            values=[
                self.factory.core.competency_matrix_item(
                    item_id=1,
                    question="Как написать свою функцию?",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    grade="Junior",
                    subsection="Функции",
                    section="Основы",
                    sheet="Python",
                ),
                self.factory.core.competency_matrix_item(
                    item_id=2,
                    question="Как написать свою функцию?",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    grade="Junior",
                    subsection="Функции",
                    section="Основы",
                    sheet="JavaScript",
                ),
            ]
        )
        response = self.api.get_competency_matrix_items(sheet_name="Java")
        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "sheet": "Java",
            "sections": [],
        }
        self.use_case.execute.assert_called_once_with(sheet_name="Java", only_published=True)

    def test_list(self) -> None:
        self.use_case.execute.return_value = self.factory.core.competency_matrix_items(
            values=[
                self.factory.core.competency_matrix_item(
                    item_id=1,
                    question="Как написать свою функцию?",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    grade="Junior",
                    subsection="Функции",
                    section="Основы",
                    sheet="Python",
                ),
            ]
        )
        response = self.api.get_competency_matrix_items(sheet_name="Python")
        assert response.status_code == codes.OK, response.content
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
        self.use_case.execute.assert_called_once_with(sheet_name="Python", only_published=True)
