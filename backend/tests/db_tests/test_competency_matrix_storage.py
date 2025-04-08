from datetime import UTC, datetime

import pytest

from db.storages import CompetencyMatrixDatabaseStorage
from tests.fixtures import FactoryFixture, StorageFixture


@pytest.mark.django_db(transaction=True)
class TestCompetencyMatrixStorage(FactoryFixture, StorageFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = CompetencyMatrixDatabaseStorage()
        self.status_changed = datetime.now(tz=UTC)
        self.db.create_competency_matrix_items(
            items=[
                self.factory.competency_matrix_item(
                    item_id=1,
                    question="1",
                    sheet="Python",
                    status_changed=self.status_changed,
                ),
                self.factory.competency_matrix_item(
                    item_id=2,
                    question="2",
                    sheet="SQL",
                    status_changed=self.status_changed,
                ),
            ],
        )

    async def test_list_sheets(self) -> None:
        sheets = await self.storage.list_sheets()
        assert sheets == ["Python", "SQL"]

    async def test_list_items(self) -> None:
        items = await self.storage.list_competency_matrix_items(sheet_name="Python")
        assert items == [
            self.factory.competency_matrix_item(
                item_id=1,
                question="1",
                sheet="Python",
                status_changed=self.status_changed,
            ),
        ]
