import datetime

import pytest_asyncio

from app.core.competency_matrix.enums import StatusEnum
from tests.fixtures import FactoryFixture, StorageFixture


class TestCompetencyMatrixStorage(StorageFixture, FactoryFixture):
    current_datetime: datetime.datetime

    @pytest_asyncio.fixture(autouse=True, loop_scope="function")
    async def setup(self) -> None:
        self.current_datetime = datetime.datetime.now(tz=datetime.UTC)
        await self.storage_helper.insert_competency_matrix_item(
            item=self.factory.full_competency_matrix_item(
                item_id=1,
                question="Range - это итератор?",
                status=StatusEnum.PUBLISHED,
                status_changed=self.current_datetime,
                answer="Почти да, но нет",
                interview_expected_answer="Нет",
                grade_id=1,
                grade=self.factory.grade(grade_id=1, name="GRADE 1"),
                subsection_id=1,
                subsection=self.factory.subsection(
                    subsection_id=1,
                    name="SUBSECTION 1",
                    section=self.factory.section(
                        section_id=1,
                        name="SECTION 1",
                        sheet=self.factory.sheet(sheet_id=1, name="SHEET 1"),
                    ),
                ),
                resources=[
                    self.factory.resource(
                        resource_id=1,
                        name="RESOURCE 1",
                        url="https://example1.com",
                        context="CONTEXT 2",
                    ),
                ],
            ),
        )
        await self.storage_helper.insert_competency_matrix_item(
            item=self.factory.full_competency_matrix_item(
                item_id=2,
                question="Что такое декоратор?",
                status=StatusEnum.PUBLISHED,
                status_changed=self.current_datetime,
                answer="Это паттерн проектирования",
                interview_expected_answer="Я не знаю",
                grade_id=2,
                grade=self.factory.grade(grade_id=1, name="GRADE 2"),
                subsection_id=2,
                subsection=self.factory.subsection(
                    subsection_id=2,
                    name="SUBSECTION 2",
                    section=self.factory.section(
                        section_id=2,
                        name="SECTION 2",
                        sheet=self.factory.sheet(sheet_id=2, name="SHEET 2"),
                    ),
                ),
                resources=[
                    self.factory.resource(
                        resource_id=2,
                        name="RESOURCE 2",
                        url="https://example2.com",
                        context="CONTEXT 2",
                    ),
                ],
            ),
        )

    async def test_get_list(self) -> None:
        items = await self.storage.list_competency_matrix_items()
        assert len(items) == 2
        assert {item.id for item in items} == {1, 2}
