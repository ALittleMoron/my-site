from unittest.mock import Mock

import pytest

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import UpsertItemUseCase
from core.enums import PublishStatusEnum
from tests.fixtures import FactoryFixture


class TestUpsertItemUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.use_case = UpsertItemUseCase(storage=self.storage)

    async def test_no_resources_to_assign(self) -> None:
        params = self.factory.core.competency_matrix_item_upsert_params(
            item_id=2,
            resources=[
                self.factory.core.external_resource(
                    resource_id=3,
                    name="resource 3",
                    url="http://example.com",
                    context="resource context 3",
                ),
            ],
        )
        await self.use_case.execute(params=params)
        self.storage.get_resources_by_ids.assert_not_called()
        self.storage.upsert_competency_matrix_item.assert_called_once_with(
            item=self.factory.core.competency_matrix_item(
                item_id=2,
                resources=[
                    self.factory.core.external_resource(
                        resource_id=3,
                        name="resource 3",
                        url="http://example.com",
                        context="resource context 3",
                    ),
                ],
            ),
        )

    async def test_not_all_resources_returned(self) -> None:
        self.storage.get_resources_by_ids.return_value = self.factory.core.external_resources(
            values=[
                self.factory.core.external_resource(
                    resource_id=1,
                    name="resource 1",
                    url="http://example1.com",
                    context="resource context 1",
                ),
            ],
        )
        params = self.factory.core.competency_matrix_item_upsert_params(
            item_id=2,
            resources=[
                self.factory.core.int_id(1),
                self.factory.core.int_id(2),
            ],
        )
        with pytest.raises(CompetencyMatrixItemNotFoundError):
            await self.use_case.execute(params=params)
        self.storage.get_resources_by_ids.assert_called_once_with(
            resource_ids=[self.factory.core.int_id(1), self.factory.core.int_id(2)],
        )
        self.storage.upsert_competency_matrix_item.assert_not_called()

    async def test_valid(self) -> None:
        self.storage.get_resources_by_ids.return_value = self.factory.core.external_resources(
            values=[
                self.factory.core.external_resource(
                    resource_id=1,
                    name="resource 1",
                    url="http://example1.com",
                    context="resource context 1",
                ),
                self.factory.core.external_resource(
                    resource_id=2,
                    name="resource 2",
                    url="http://example2.com",
                    context="resource context 2",
                ),
            ],
        )
        params = self.factory.core.competency_matrix_item_upsert_params(
            item_id=2,
            question="2",
            publish_status=PublishStatusEnum.DRAFT,
            sheet="Python",
            grade="",
            section="",
            subsection="",
            resources=[
                self.factory.core.int_id(1),
                self.factory.core.int_id(2),
                self.factory.core.external_resource(
                    resource_id=3,
                    name="resource 3",
                    url="http://example.com",
                    context="resource context 3",
                ),
            ],
        )
        await self.use_case.execute(params=params)
        self.storage.get_resources_by_ids.assert_called_once_with(
            resource_ids=[self.factory.core.int_id(1), self.factory.core.int_id(2)],
        )
        self.storage.upsert_competency_matrix_item.assert_called_once_with(
            item=self.factory.core.competency_matrix_item(
                item_id=2,
                question="2",
                publish_status=PublishStatusEnum.DRAFT,
                sheet="Python",
                grade="",
                section="",
                subsection="",
                resources=[
                    self.factory.core.external_resource(
                        resource_id=1,
                        name="resource 1",
                        url="http://example1.com",
                        context="resource context 1",
                    ),
                    self.factory.core.external_resource(
                        resource_id=2,
                        name="resource 2",
                        url="http://example2.com",
                        context="resource context 2",
                    ),
                    self.factory.core.external_resource(
                        resource_id=3,
                        name="resource 3",
                        url="http://example.com",
                        context="resource context 3",
                    ),
                ],
            ),
        )
