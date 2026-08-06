from datetime import UTC, datetime

import pytest
import pytest_asyncio

from core.auth.enums import RoleEnum
from core.knowledge.dates.enums import KnowledgeDateListSort
from core.knowledge.dates.schemas import (
    KnowledgeDateCreateParams,
    KnowledgeDateFilters,
    KnowledgeDateUpdateParams,
    KnowledgeDateValue,
)
from core.knowledge.dates.use_cases import KnowledgeDatesUseCase
from core.knowledge.exceptions import (
    KnowledgeFileNotFoundError,
    KnowledgeItemNotFoundError,
    PersonNotFoundError,
)
from core.knowledge.files.enums import KnowledgeFileKind
from core.knowledge.files.schemas import KnowledgeFile
from core.knowledge.items.schemas import KnowledgeTagCreateParams
from core.knowledge.items.services import KnowledgeItemCrudService
from core.knowledge.items.use_cases import KnowledgeTagsUseCase
from core.knowledge.people.schemas import PersonQuickCreateParams
from core.knowledge.people.use_cases import PeopleUseCase
from infra.postgresql.storages.knowledge.dates import KnowledgeDatesDatabaseStorage
from infra.postgresql.storages.knowledge.files import KnowledgeFilesDatabaseStorage
from infra.postgresql.storages.knowledge.items import KnowledgeItemsDatabaseStorage
from infra.postgresql.storages.knowledge.people import PeopleDatabaseStorage
from tests.test_cases import StorageTestCase

CURRENT_DATETIME = datetime(2026, 7, 30, 12, 0, tzinfo=UTC)


class TestKnowledgeDatesStorage(StorageTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        await self.storage_helper.create_users(
            users=[
                self.factory.core.user(
                    username="admin",
                    password_hash="hash",  # noqa: S106
                    role=RoleEnum.ADMIN,
                ),
                self.factory.core.user(
                    username="other-admin",
                    password_hash="hash",  # noqa: S106
                    role=RoleEnum.ADMIN,
                ),
            ],
        )
        self.item_storage = KnowledgeItemsDatabaseStorage(session=self.db_session)
        self.dates_storage = KnowledgeDatesDatabaseStorage(session=self.db_session)
        self.people_storage = PeopleDatabaseStorage(session=self.db_session)
        self.file_storage = KnowledgeFilesDatabaseStorage(session=self.db_session)
        self.item_service = KnowledgeItemCrudService(storage=self.item_storage)
        self.dates_use_case = KnowledgeDatesUseCase(
            item_service=self.item_service,
            item_storage=self.item_storage,
            dates_storage=self.dates_storage,
            file_storage=self.file_storage,
        )
        self.people_use_case = PeopleUseCase(
            item_service=self.item_service,
            item_storage=self.item_storage,
            people_storage=self.people_storage,
            dates_storage=self.dates_storage,
            file_storage=self.file_storage,
        )
        self.tags_use_case = KnowledgeTagsUseCase(storage=self.item_storage)

    async def test_crud_filters_backlinks_and_person_delete_cascade(self) -> None:
        person = await self.people_use_case.create_person(
            params=PersonQuickCreateParams(
                first_name="Иван",
                last_name="Иванов",
                author_username="admin",
            ),
        )
        tag = await self.tags_use_case.create_tag(
            params=KnowledgeTagCreateParams(
                author_username="admin",
                name="Семья",
            ),
        )
        january = await self.dates_use_case.create_date(
            params=KnowledgeDateCreateParams(
                display_name="Новый год",
                date=KnowledgeDateValue(day=1, month=1, year=None),
                author_username="admin",
            ),
            today=CURRENT_DATETIME.date(),
        )
        december = await self.dates_use_case.create_date(
            params=KnowledgeDateCreateParams(
                display_name="Годовщина",
                date=KnowledgeDateValue(day=31, month=12, year=2020),
                author_username="admin",
            ),
            today=CURRENT_DATETIME.date(),
        )
        december = await self.dates_use_case.update_date(
            date_id=december.item.id,
            params=KnowledgeDateUpdateParams(
                display_name="Годовщина",
                date=KnowledgeDateValue(day=31, month=12, year=2020),
                description="Приватное описание",
                tag_ids=[tag.id],
                person_ids=[person.item.id],
            ),
            author_username="admin",
            current_datetime=CURRENT_DATETIME,
        )

        ascending = await self.dates_use_case.list_dates(
            filters=KnowledgeDateFilters(
                page=1,
                page_size=1,
                sort=KnowledgeDateListSort.DATE_ASC,
                search_query=None,
                tag_ids=(),
                related_person_id=None,
                author_username="admin",
            ),
        )
        filtered = await self.dates_use_case.list_dates(
            filters=KnowledgeDateFilters(
                page=1,
                page_size=20,
                sort=KnowledgeDateListSort.DATE_DESC,
                search_query="годов",
                tag_ids=(tag.id,),
                related_person_id=person.item.id,
                author_username="admin",
            ),
        )
        person_with_backlink = await self.people_use_case.get_person(
            person_id=person.item.id,
            author_username="admin",
        )

        assert ascending.total_count == 2
        assert ascending.total_pages == 2
        assert [value.id for value in ascending.values] == [january.item.id]
        assert [value.id for value in filtered.values] == [december.item.id]
        assert filtered.values[0].related_people[0].id == person.item.id
        assert [value.id for value in person_with_backlink.related_dates] == [
            december.item.id,
        ]

        before_person_delete = december.item.updated_at
        await self.people_use_case.delete_person(
            person_id=person.item.id,
            author_username="admin",
            current_datetime=CURRENT_DATETIME,
        )
        date_after_person_delete = await self.dates_use_case.get_date(
            date_id=december.item.id,
            author_username="admin",
        )
        assert date_after_person_delete.related_people == []
        assert date_after_person_delete.item.updated_at >= before_person_delete

    async def test_author_kind_guards_and_attachment_delete_cleanup(self) -> None:
        own_person = await self.people_use_case.create_person(
            params=PersonQuickCreateParams(
                first_name="Иван",
                last_name="Иванов",
                author_username="admin",
            ),
        )
        foreign_person = await self.people_use_case.create_person(
            params=PersonQuickCreateParams(
                first_name="Пётр",
                last_name="Петров",
                author_username="other-admin",
            ),
        )
        own_date = await self.dates_use_case.create_date(
            params=KnowledgeDateCreateParams(
                display_name="Событие",
                date=KnowledgeDateValue(day=1, month=5, year=2020),
                author_username="admin",
            ),
            today=CURRENT_DATETIME.date(),
        )
        foreign_date = await self.dates_use_case.create_date(
            params=KnowledgeDateCreateParams(
                display_name="Чужое событие",
                date=KnowledgeDateValue(day=2, month=5, year=2020),
                author_username="other-admin",
            ),
            today=CURRENT_DATETIME.date(),
        )

        with pytest.raises(PersonNotFoundError):
            await self.dates_use_case.update_date(
                date_id=own_date.item.id,
                params=KnowledgeDateUpdateParams(
                    display_name="Событие",
                    date=KnowledgeDateValue(day=1, month=5, year=2020),
                    description="",
                    tag_ids=[],
                    person_ids=[foreign_person.item.id],
                ),
                author_username="admin",
                current_datetime=CURRENT_DATETIME,
            )
        with pytest.raises(KnowledgeItemNotFoundError):
            await self.dates_use_case.get_date(
                date_id=foreign_date.item.id,
                author_username="admin",
            )
        with pytest.raises(KnowledgeItemNotFoundError):
            await self.dates_use_case.get_date(
                date_id=own_person.item.id,
                author_username="admin",
            )

        now = datetime.now(tz=UTC)
        file = await self.file_storage.create_file(
            file=KnowledgeFile(
                id="f" * 32,
                item_id=own_date.item.id,
                author_username="admin",
                kind=KnowledgeFileKind.ATTACHMENT,
                relative_path="attachments/date-private.txt",
                mime_type="text/plain",
                size_bytes=7,
                name="Private",
                original_name="private.txt",
                original_sha256="a" * 64,
                created_at=now,
                updated_at=now,
            ),
        )

        object_names = await self.dates_use_case.delete_date(
            date_id=own_date.item.id,
            author_username="admin",
            current_datetime=CURRENT_DATETIME,
        )

        assert object_names == ("attachments/date-private.txt",)
        with pytest.raises(KnowledgeFileNotFoundError):
            await self.file_storage.get_file(
                file_id=file.id,
                author_username="admin",
            )

    async def test_list_details_for_months_is_author_scoped(self) -> None:
        own_july = await self.dates_use_case.create_date(
            params=KnowledgeDateCreateParams(
                display_name="Июль",
                date=KnowledgeDateValue(day=31, month=7, year=None),
                author_username="admin",
            ),
            today=CURRENT_DATETIME.date(),
        )
        own_august = await self.dates_use_case.create_date(
            params=KnowledgeDateCreateParams(
                display_name="Август",
                date=KnowledgeDateValue(day=1, month=8, year=None),
                author_username="admin",
            ),
            today=CURRENT_DATETIME.date(),
        )
        await self.dates_use_case.create_date(
            params=KnowledgeDateCreateParams(
                display_name="Сентябрь",
                date=KnowledgeDateValue(day=1, month=9, year=None),
                author_username="admin",
            ),
            today=CURRENT_DATETIME.date(),
        )
        await self.dates_use_case.create_date(
            params=KnowledgeDateCreateParams(
                display_name="Чужой август",
                date=KnowledgeDateValue(day=2, month=8, year=None),
                author_username="other-admin",
            ),
            today=CURRENT_DATETIME.date(),
        )

        details = await self.dates_storage.list_details_for_months(
            months=(7, 8),
            author_username="admin",
        )

        assert [value.item_id for value in details] == [own_july.item.id, own_august.item.id]
