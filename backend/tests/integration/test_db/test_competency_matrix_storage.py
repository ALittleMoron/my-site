import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import IntId
from infra.postgresql.storages.competency_matrix import CompetencyMatrixDatabaseStorage
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
                    grade=GradeEnum.MIDDLE_PLUS,
                    section="SECTION 1",
                    subsection="SUBSECTION 1",
                    resources=[
                        self.factory.core.attached_external_resource(
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
                    grade=GradeEnum.SENIOR,
                    section="SECTION 2",
                    subsection="SUBSECTION 2",
                    resources=[
                        self.factory.core.attached_external_resource(
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
        assert sheets == self.factory.core.sheets(values=["Python", "SQL"])

    async def test_list_items(self) -> None:
        items = await self.storage.list_competency_matrix_items(sheet_key="python")
        assert items == [
            self.factory.core.competency_matrix_item(
                item_id=1,
                question="1",
                answer="Answer 1",
                interview_expected_answer="Expected answer 1",
                sheet="Python",
                grade=GradeEnum.MIDDLE_PLUS,
                section="SECTION 1",
                subsection="SUBSECTION 1",
                resources=[],
            ),
        ]

    async def test_get_competency_matrix_item_not_found(self) -> None:
        with pytest.raises(CompetencyMatrixItemNotFoundError):
            await self.storage.get_competency_matrix_item(item_id=self.factory.core.int_id(-1))

    async def test_get_competency_matrix_item_found(self) -> None:
        item = await self.storage.get_competency_matrix_item(item_id=self.factory.core.int_id(1))
        assert item == self.factory.core.competency_matrix_item(
            item_id=1,
            question="1",
            answer="Answer 1",
            interview_expected_answer="Expected answer 1",
            sheet="Python",
            grade=GradeEnum.MIDDLE_PLUS,
            section="SECTION 1",
            subsection="SUBSECTION 1",
            resources=[
                self.factory.core.attached_external_resource(
                    resource_id=1,
                    name="NAME 1",
                    url="https://example1.com",
                    context="CONTEXT 1",
                ),
            ],
        )

    async def test_create_competency_matrix_item(self) -> None:
        item = await self.storage.create_competency_matrix_item(
            item=self.factory.core.competency_matrix_item(
                item_id=3,
                question="1",
                answer="Answer 1",
                interview_expected_answer="Expected answer 1",
                sheet="Python",
                grade=GradeEnum.MIDDLE_PLUS,
                section="SECTION 1",
                subsection="SUBSECTION 1",
                resources=[
                    self.factory.core.attached_external_resource(
                        resource_id=10,
                        name="NAME 1",
                        url="https://example1.com",
                        context="CONTEXT 1",
                    ),
                ],
            ),
        )
        assert item == self.factory.core.competency_matrix_item(
            item_id=3,
            question="1",
            answer="Answer 1",
            interview_expected_answer="Expected answer 1",
            sheet="Python",
            grade=GradeEnum.MIDDLE_PLUS,
            section="SECTION 1",
            subsection="SUBSECTION 1",
            resources=[
                self.factory.core.attached_external_resource(
                    resource_id=10,
                    name="NAME 1",
                    url="https://example1.com",
                    context="CONTEXT 1",
                ),
            ],
        )

    async def test_update_competency_matrix_item(self) -> None:
        await self.storage_helper.create_competency_matrix_items(
            items=[
                self.factory.core.competency_matrix_item(
                    item_id=3,
                    question="1",
                    answer="Answer 1",
                    interview_expected_answer="Expected answer 1",
                    sheet="Python",
                    grade=GradeEnum.MIDDLE_PLUS,
                    section="SECTION 1",
                    subsection="SUBSECTION 1",
                    resources=[
                        self.factory.core.attached_external_resource(
                            resource_id=10,
                            name="NAME 1",
                            url="https://example1.com",
                            context="CONTEXT 1",
                        ),
                    ],
                ),
            ],
        )
        item = await self.storage.update_competency_matrix_item(
            item=self.factory.core.competency_matrix_item(
                item_id=3,
                question="3",
                answer="Answer 3",
                interview_expected_answer="Expected answer 3",
                sheet="Python 2",
                grade=GradeEnum.SENIOR,
                section="SECTION 3",
                subsection="SUBSECTION 3",
                resources=[
                    self.factory.core.attached_external_resource(
                        resource_id=10,
                        name="NAME 3",
                        url="https://example3.com",
                        context="CONTEXT 3",
                    ),
                ],
            ),
        )
        assert item == self.factory.core.competency_matrix_item(
            item_id=3,
            question="3",
            answer="Answer 3",
            interview_expected_answer="Expected answer 3",
            sheet="Python 2",
            grade=GradeEnum.SENIOR,
            section="SECTION 3",
            subsection="SUBSECTION 3",
            resources=[
                self.factory.core.attached_external_resource(
                    resource_id=10,
                    name="NAME 3",
                    url="https://example3.com",
                    context="CONTEXT 3",
                ),
            ],
        )

    async def test_update_competency_matrix_item_replaces_resources(self) -> None:
        await self.storage_helper.create_competency_matrix_items(
            items=[
                self.factory.core.competency_matrix_item(
                    item_id=3,
                    question="1",
                    answer="Answer 1",
                    interview_expected_answer="Expected answer 1",
                    sheet="Python",
                    grade=GradeEnum.MIDDLE_PLUS,
                    section="SECTION 1",
                    subsection="SUBSECTION 1",
                    resources=[
                        self.factory.core.attached_external_resource(
                            resource_id=10,
                            name="NAME 10",
                            url="https://example10.com",
                            context="CONTEXT 10",
                        ),
                        self.factory.core.attached_external_resource(
                            resource_id=11,
                            name="NAME 11",
                            url="https://example11.com",
                            context="CONTEXT 11",
                        ),
                    ],
                ),
            ],
        )
        item = await self.storage.update_competency_matrix_item(
            item=self.factory.core.competency_matrix_item(
                item_id=3,
                question="1",
                answer="Answer 1",
                interview_expected_answer="Expected answer 1",
                sheet="Python",
                grade=GradeEnum.MIDDLE_PLUS,
                section="SECTION 1",
                subsection="SUBSECTION 1",
                resources=[
                    self.factory.core.attached_external_resource(
                        resource_id=12,
                        name="NAME 12",
                        url="https://example12.com",
                        context="CONTEXT 12",
                    ),
                ],
            ),
        )
        assert item.resources.values == [
            self.factory.core.attached_external_resource(
                resource_id=12,
                name="NAME 12",
                url="https://example12.com",
                context="CONTEXT 12",
            ),
        ]

    async def test_update_competency_matrix_item_not_found(self) -> None:
        with pytest.raises(CompetencyMatrixItemNotFoundError):
            await self.storage.update_competency_matrix_item(
                item=self.factory.core.competency_matrix_item(item_id=3),
            )

    async def test_update_publish_status(self) -> None:
        await self.storage_helper.create_competency_matrix_items(
            items=[
                self.factory.core.competency_matrix_item(
                    item_id=3,
                    question="1",
                    answer="Answer 1",
                    interview_expected_answer="Expected answer 1",
                    sheet="Python",
                    grade=GradeEnum.MIDDLE_PLUS,
                    section="SECTION 1",
                    subsection="SUBSECTION 1",
                    publish_status=PublishStatusEnum.PUBLISHED,
                ),
            ],
        )
        await self.storage.update_competency_matrix_item_publish_status(
            item_id=self.factory.core.int_id(3),
            publish_status=PublishStatusEnum.DRAFT,
        )
        item = await self.storage.get_competency_matrix_item(item_id=self.factory.core.int_id(3))
        assert item.publish_status == PublishStatusEnum.DRAFT

    async def test_update_publish_status_not_found(self) -> None:
        with pytest.raises(CompetencyMatrixItemNotFoundError):
            await self.storage.update_competency_matrix_item_publish_status(
                item_id=self.factory.core.int_id(3),
                publish_status=PublishStatusEnum.DRAFT,
            )

    async def test_get_resources_by_ids(self) -> None:
        await self.storage_helper.create_external_resources(
            resources=[
                self.factory.core.external_resource(
                    resource_id=100,
                    name="NAME 100",
                    url="https://example100.com",
                ),
                self.factory.core.external_resource(
                    resource_id=101,
                    name="NAME 101",
                    url="https://example101.com",
                ),
            ],
        )
        resources = await self.storage.get_resources_by_ids(resource_ids=[IntId(100), IntId(101)])
        assert resources.values == [
            self.factory.core.external_resource(
                resource_id=100,
                name="NAME 100",
                url="https://example100.com",
            ),
            self.factory.core.external_resource(
                resource_id=101,
                name="NAME 101",
                url="https://example101.com",
            ),
        ]

    async def test_delete_found(self) -> None:
        await self.storage_helper.create_competency_matrix_items(
            items=[
                self.factory.core.competency_matrix_item(
                    item_id=3,
                    question="1",
                    answer="Answer 1",
                    interview_expected_answer="Expected answer 1",
                    sheet="Python",
                    grade=GradeEnum.MIDDLE_PLUS,
                    section="SECTION 1",
                    subsection="SUBSECTION 1",
                    resources=[
                        self.factory.core.attached_external_resource(
                            resource_id=10,
                            name="NAME 1",
                            url="https://example1.com",
                            context="CONTEXT 1",
                        ),
                    ],
                ),
            ],
        )
        await self.storage.delete_competency_matrix_item(item_id=self.factory.core.int_id(3))
        with pytest.raises(CompetencyMatrixItemNotFoundError):
            await self.storage.get_competency_matrix_item(item_id=self.factory.core.int_id(3))

    async def test_delete_not_found(self) -> None:
        with pytest.raises(CompetencyMatrixItemNotFoundError):
            await self.storage.delete_competency_matrix_item(item_id=self.factory.core.int_id(3))

    async def test_search_competency_matrix_resources(self) -> None:
        await self.storage_helper.create_external_resources(
            resources=[
                self.factory.core.external_resource(
                    resource_id=100,
                    name="NAMED 100",
                    url="https://example100.com",
                ),
                self.factory.core.external_resource(
                    resource_id=101,
                    name="NAMED 101",
                    url="https://example101.com",
                ),
                self.factory.core.external_resource(
                    resource_id=102,
                    name="NOT HAS N*MED",
                    url="https://example102.com",
                ),
            ],
        )
        resources = await self.storage.search_competency_matrix_resources(
            search_name="named",
            limit=10,
            language=LanguageEnum.EN,
        )
        assert len(resources) == 2
        assert resources[0].name_en == "NAMED 100"
        assert resources[1].name_en == "NAMED 101"

    async def test_search_competency_matrix_resources_matches_typo(self) -> None:
        await self.storage_helper.create_external_resources(
            resources=[
                self.factory.core.external_resource(
                    resource_id=110,
                    name="Pydantic",
                    url="https://docs.pydantic.dev",
                ),
                self.factory.core.external_resource(
                    resource_id=111,
                    name="Django",
                    url="https://docs.djangoproject.com",
                ),
            ],
        )
        resources = await self.storage.search_competency_matrix_resources(
            search_name="pydntic",
            limit=10,
            language=LanguageEnum.EN,
        )
        assert [resource.name_en for resource in resources] == ["Pydantic"]

    async def test_search_competency_matrix_resources_matches_secondary_language_name(
        self,
    ) -> None:
        await self.storage_helper.create_external_resources(
            resources=[
                self.factory.core.external_resource(
                    resource_id=120,
                    name_ru="Документация FastAPI",
                    name_en="FastAPI docs",
                    url="https://fastapi.tiangolo.com",
                ),
            ],
        )
        resources = await self.storage.search_competency_matrix_resources(
            search_name="документация",
            limit=10,
            language=LanguageEnum.EN,
        )
        assert [resource.name_en for resource in resources] == ["FastAPI docs"]

    async def test_search_competency_matrix_resources_ranks_active_language_matches(
        self,
    ) -> None:
        await self.storage_helper.create_external_resources(
            resources=[
                self.factory.core.external_resource(
                    resource_id=130,
                    name="Python Package Index",
                    url="https://pypi.org",
                ),
                self.factory.core.external_resource(
                    resource_id=131,
                    name="Packaging guide",
                    url="https://python.example.com/packages",
                ),
                self.factory.core.external_resource(
                    resource_id=132,
                    name="Python",
                    url="https://python.org",
                ),
            ],
        )
        resources = await self.storage.search_competency_matrix_resources(
            search_name="python",
            limit=10,
            language=LanguageEnum.EN,
        )
        assert [resource.name_en for resource in resources][:2] == [
            "Python",
            "Python Package Index",
        ]

    async def test_search_competency_matrix_resources_respects_limit(self) -> None:
        await self.storage_helper.create_external_resources(
            resources=[
                self.factory.core.external_resource(
                    resource_id=140,
                    name="Limit resource A",
                    url="https://example-a.com",
                ),
                self.factory.core.external_resource(
                    resource_id=141,
                    name="Limit resource B",
                    url="https://example-b.com",
                ),
                self.factory.core.external_resource(
                    resource_id=142,
                    name="Limit resource C",
                    url="https://example-c.com",
                ),
            ],
        )
        resources = await self.storage.search_competency_matrix_resources(
            search_name="limit",
            limit=2,
            language=LanguageEnum.EN,
        )
        assert len(resources) == 2
