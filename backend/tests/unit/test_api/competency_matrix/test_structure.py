import pytest_asyncio
from httpx import codes

from core.competency_matrix.schemas import (
    CompetencyMatrixStructure,
    CompetencyMatrixStructureSection,
    CompetencyMatrixStructureSheet,
    CompetencyMatrixStructureSubsection,
)
from tests.test_cases import ApiTestCase


class TestMatrixStructureAPI(ApiTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_competency_matrix_use_case()

    def test_lists_admin_structure_tree(self) -> None:
        self.use_case.list_structure.return_value = CompetencyMatrixStructure(
            sheets=[
                CompetencyMatrixStructureSheet(
                    id=self.factory.core.int_id(1),
                    key="python",
                    name_ru="Питон",
                    name_en="Python",
                    sections=[
                        CompetencyMatrixStructureSection(
                            id=self.factory.core.int_id(2),
                            name_ru="Основы",
                            name_en="Basics",
                            subsections=[
                                CompetencyMatrixStructureSubsection(
                                    id=self.factory.core.int_id(3),
                                    name_ru="Функции",
                                    name_en="Functions",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

        response = self.api.client.get(
            "/api/admin/competency-matrix/structure",
            params={"language": "en"},
        )

        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "sheets": [
                {
                    "id": 1,
                    "key": "python",
                    "name": "Python",
                    "translations": {
                        "ru": {"name": "Питон"},
                        "en": {"name": "Python"},
                    },
                    "sections": [
                        {
                            "id": 2,
                            "name": "Basics",
                            "translations": {
                                "ru": {"name": "Основы"},
                                "en": {"name": "Basics"},
                            },
                            "subsections": [
                                {
                                    "id": 3,
                                    "name": "Functions",
                                    "translations": {
                                        "ru": {"name": "Функции"},
                                        "en": {"name": "Functions"},
                                    },
                                },
                            ],
                        },
                    ],
                },
            ],
        }
        self.use_case.list_structure.assert_called_once_with()

    def test_creates_sheet_section_and_subsection(self) -> None:
        self.use_case.create_sheet.return_value = CompetencyMatrixStructureSheet(
            id=self.factory.core.int_id(1),
            key="python",
            name_ru="Питон",
            name_en="Python",
            sections=[],
        )
        self.use_case.create_section.return_value = CompetencyMatrixStructureSection(
            id=self.factory.core.int_id(2),
            name_ru="Основы",
            name_en="Basics",
            subsections=[],
        )
        self.use_case.create_subsection.return_value = CompetencyMatrixStructureSubsection(
            id=self.factory.core.int_id(3),
            name_ru="Функции",
            name_en="Functions",
        )

        sheet_response = self.api.client.post(
            "/api/admin/competency-matrix/sheets",
            params={"language": "en"},
            json={
                "key": "python",
                "translations": {
                    "ru": {"name": "Питон"},
                    "en": {"name": "Python"},
                },
            },
        )
        section_response = self.api.client.post(
            "/api/admin/competency-matrix/sheets/1/sections",
            params={"language": "en"},
            json={
                "translations": {
                    "ru": {"name": "Основы"},
                    "en": {"name": "Basics"},
                },
            },
        )
        subsection_response = self.api.client.post(
            "/api/admin/competency-matrix/sections/2/subsections",
            params={"language": "en"},
            json={
                "translations": {
                    "ru": {"name": "Функции"},
                    "en": {"name": "Functions"},
                },
            },
        )

        assert sheet_response.status_code == codes.CREATED, sheet_response.content
        assert section_response.status_code == codes.CREATED, section_response.content
        assert subsection_response.status_code == codes.CREATED, subsection_response.content
        assert sheet_response.json()["key"] == "python"
        assert section_response.json()["name"] == "Basics"
        assert subsection_response.json()["name"] == "Functions"

    def test_structure_endpoints_are_admin_only(self) -> None:
        response = self.no_auth_api.client.get(
            "/api/competency-matrix/structure",
            params={"language": "ru"},
        )
        assert response.status_code == codes.NOT_FOUND

        response = self.no_auth_api.client.post(
            "/api/competency-matrix/sheets",
            params={"language": "ru"},
            json={
                "key": "python",
                "translations": {
                    "ru": {"name": "Питон"},
                    "en": {"name": "Python"},
                },
            },
        )
        assert response.status_code == codes.METHOD_NOT_ALLOWED
