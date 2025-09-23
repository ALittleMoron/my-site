import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.enums import PublishStatusEnum
from db.storages.competency_matrix import CompetencyMatrixDatabaseStorage
from tests.fixtures import FactoryFixture, StorageFixture


class TestCompetencyMatrixStorage(FactoryFixture, StorageFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, session: AsyncSession) -> None:
        self.storage = CompetencyMatrixDatabaseStorage(session=session)
        await self.storage_helper.create_competency_matrix_items(
            items=[
                self.factory.core.competency_matrix_item(
                    item_id=1,
                    question="1",
                    answer="Answer 1",
                    interview_expected_answer="Expected answer 1",
                    sheet="Python",
                    grade="Middle+",
                    section="SECTION 1",
                    subsection="SUBSECTION 1",
                    resources=[
                        self.factory.core.resource(
                            resource_id=1,
                            name="NAME 1",
                            url="https://example1.com",
                            context="CONTEXT 1",
                        ),
                    ],
                ),
                self.factory.core.competency_matrix_item(
                    item_id=2,
                    question="2",
                    answer="Answer 2",
                    interview_expected_answer="Expected answer 2",
                    sheet="SQL",
                    grade="Senior",
                    section="SECTION 2",
                    subsection="SUBSECTION 2",
                    resources=[
                        self.factory.core.resource(
                            resource_id=2,
                            name="NAME 2",
                            url="https://example2.com",
                            context="CONTEXT 2",
                        ),
                    ],
                ),
            ],
        )

    async def test_list_sheets(self) -> None:
        sheets = await self.storage.list_sheets()
        assert sheets == ["Python", "SQL"]

    async def test_list_items_only_available(self) -> None:
        await self.storage_helper.create_competency_matrix_items(
            items=[
                self.factory.core.competency_matrix_item(
                    item_id=3,
                    sheet="JS",
                    publish_status=PublishStatusEnum.PUBLISHED,
                ),
                self.factory.core.competency_matrix_item(
                    item_id=4,
                    sheet="JS",
                    publish_status=PublishStatusEnum.DRAFT,
                ),
            ],
        )
        items = await self.storage.list_competency_matrix_items(sheet_name="JS")
        assert items == [
            self.factory.core.competency_matrix_item(
                item_id=3,
                sheet="JS",
                publish_status=PublishStatusEnum.PUBLISHED,
            ),
        ]

    async def test_list_items(self) -> None:
        items = await self.storage.list_competency_matrix_items(sheet_name="Python")
        assert items == [
            self.factory.core.competency_matrix_item(
                item_id=1,
                question="1",
                answer="Answer 1",
                interview_expected_answer="Expected answer 1",
                sheet="Python",
                grade="Middle+",
                section="SECTION 1",
                subsection="SUBSECTION 1",
                resources=[],
            ),
        ]

    async def test_get_competency_matrix_item_not_found(self) -> None:
        with pytest.raises(CompetencyMatrixItemNotFoundError):
            await self.storage.get_competency_matrix_item(item_id=-1)

    async def test_get_competency_matrix_item_found(self) -> None:
        item = await self.storage.get_competency_matrix_item(item_id=1)
        assert item == self.factory.core.competency_matrix_item(
            item_id=1,
            question="1",
            answer="Answer 1",
            interview_expected_answer="Expected answer 1",
            sheet="Python",
            grade="Middle+",
            section="SECTION 1",
            subsection="SUBSECTION 1",
            resources=[
                self.factory.core.resource(
                    resource_id=1,
                    name="NAME 1",
                    url="https://example1.com",
                    context="CONTEXT 1",
                ),
            ],
        )
