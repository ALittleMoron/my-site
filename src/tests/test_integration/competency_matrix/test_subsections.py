import pytest_asyncio

from tests.fixtures import ApiFixture, FactoryFixture, StorageFixture


class TestCompetencyMatrixSheet(ApiFixture, FactoryFixture, StorageFixture):
    @pytest_asyncio.fixture(autouse=True, loop_scope="function")
    async def setup(self) -> None:
        await self.storage_helper.insert_subsection(
            subsection=self.factory.subsection(
                subsection_id=1,
                name="Функции",
                section=self.factory.section(
                    section_id=1,
                    name="Основы",
                    sheet=self.factory.sheet(sheet_id=1, name="Python"),
                ),
            ),
        )
        await self.storage_helper.insert_subsection(
            subsection=self.factory.subsection(
                subsection_id=2,
                name="Протоколы",
                section=self.factory.section(
                    section_id=2,
                    name="ООП",
                    sheet=self.factory.sheet(sheet_id=2, name="JavaScript"),
                ),
            ),
        )

    async def test_list(self) -> None:
        response = self.api.list_competency_matrix_subsections(sheet_id=1)
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
            ],
        }
