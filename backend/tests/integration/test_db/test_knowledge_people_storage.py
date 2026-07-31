from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import event, insert
from sqlalchemy.engine import Connection

from core.auth.enums import RoleEnum
from core.knowledge.dates.storages import KnowledgeDatesStorage
from core.knowledge.exceptions import (
    KnowledgeConflictError,
    KnowledgeFileNotFoundError,
    KnowledgeItemNotFoundError,
    PersonRelationshipNotFoundError,
)
from core.knowledge.files.enums import KnowledgeFileKind
from core.knowledge.files.schemas import KnowledgeFile
from core.knowledge.items.enums import KnowledgeItemKind
from core.knowledge.items.schemas import KnowledgeTagCreateParams
from core.knowledge.items.services import KnowledgeItemCrudService
from core.knowledge.items.use_cases import KnowledgeTagsUseCase
from core.knowledge.people.enums import (
    PersonListSort,
    PersonRelationshipDirection,
)
from core.knowledge.people.schemas import (
    PersonFilters,
    PersonQuickCreateParams,
    PersonRelationshipChanges,
    PersonRelationshipCreateParams,
    PersonRelationshipTypeCreateParams,
    PersonRelationshipUpdateParams,
    PersonUpdateParams,
)
from core.knowledge.people.use_cases import (
    PeopleUseCase,
    PersonRelationshipTypesUseCase,
)
from infra.postgresql.models import KnowledgeItemModel, PersonDetailsModel
from infra.postgresql.storages.knowledge.dates import KnowledgeDatesDatabaseStorage
from infra.postgresql.storages.knowledge.files import KnowledgeFilesDatabaseStorage
from infra.postgresql.storages.knowledge.items import KnowledgeItemsDatabaseStorage
from infra.postgresql.storages.knowledge.people import (
    PeopleDatabaseStorage,
)
from tests.test_cases import StorageTestCase

BROAD_MATCH_COUNT = 33_000


def person_update(
    *,
    last_name: str,
    first_name: str,
    contacts: tuple[str, str, str] = ("", "", ""),
    tag_ids: list[str] | None = None,
    relationship_changes: PersonRelationshipChanges | None = None,
) -> PersonUpdateParams:
    email, phone, telegram = contacts
    return PersonUpdateParams(
        last_name=last_name,
        first_name=first_name,
        middle_name="",
        email=email,
        phone=phone,
        telegram=telegram,
        birthday=None,
        description="",
        tag_ids=tag_ids or [],
        relationship_changes=relationship_changes
        or PersonRelationshipChanges(create=[], update=[], delete_ids=[]),
    )


class TestKnowledgePeopleStorage(StorageTestCase):
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
        self.people_storage = PeopleDatabaseStorage(session=self.db_session)
        self.dates_storage: KnowledgeDatesStorage = KnowledgeDatesDatabaseStorage(
            session=self.db_session,
        )
        self.file_storage = KnowledgeFilesDatabaseStorage(session=self.db_session)
        self.item_service = KnowledgeItemCrudService(storage=self.item_storage)
        self.people_use_case = PeopleUseCase(
            item_service=self.item_service,
            item_storage=self.item_storage,
            people_storage=self.people_storage,
            dates_storage=self.dates_storage,
            file_storage=self.file_storage,
        )
        self.tags_use_case = KnowledgeTagsUseCase(storage=self.item_storage)
        self.relationship_types_use_case = PersonRelationshipTypesUseCase(
            storage=self.people_storage,
        )

    async def test_quick_create_and_foreign_guessed_ids_are_author_isolated(self) -> None:
        own = await self.people_use_case.create_person(
            params=PersonQuickCreateParams(
                first_name="Иван",
                last_name="Иванов",
                author_username="admin",
            ),
        )
        foreign = await self.people_use_case.create_person(
            params=PersonQuickCreateParams(
                first_name="Пётр",
                last_name="Петров",
                author_username="other-admin",
            ),
        )

        assert own.item.display_name == "Иванов Иван"
        assert own.item.description == ""
        assert own.details.middle_name == ""
        assert own.details.email == ""
        assert own.details.phone == ""
        assert own.details.telegram == ""
        assert own.details.birthday is None

        listed = await self.people_use_case.list_people(
            filters=PersonFilters(
                page=1,
                page_size=20,
                sort=PersonListSort.UPDATED_NEWEST,
                search_query=None,
                tag_ids=(),
                author_username="admin",
            ),
        )

        assert [person.id for person in listed.values] == [own.item.id]
        with pytest.raises(KnowledgeItemNotFoundError):
            await self.people_use_case.get_person(
                person_id=foreign.item.id,
                author_username="admin",
            )
        with pytest.raises(KnowledgeItemNotFoundError):
            await self.people_use_case.delete_person(
                person_id=foreign.item.id,
                author_username="admin",
            )

    async def test_search_and_tag_and_filters_sort_paginate_without_n_plus_one(self) -> None:
        work = await self.tags_use_case.create_tag(
            params=KnowledgeTagCreateParams(name="Работа", author_username="admin"),
        )
        close = await self.tags_use_case.create_tag(
            params=KnowledgeTagCreateParams(name="Близкие", author_username="admin"),
        )
        people = []
        for last_name, first_name, email, tag_ids in (
            ("Альфа", "Анна", "anna@example.com", [work.id, close.id]),
            ("Бета", "Борис", "boris@example.com", [work.id]),
            ("Гамма", "Галина", "galina@example.com", [work.id, close.id]),
        ):
            person = await self.people_use_case.create_person(
                params=PersonQuickCreateParams(
                    first_name=first_name,
                    last_name=last_name,
                    author_username="admin",
                ),
            )
            await self.people_use_case.update_person(
                person_id=person.item.id,
                params=person_update(
                    last_name=last_name,
                    first_name=first_name,
                    contacts=(email, "", ""),
                    tag_ids=tag_ids,
                ),
                author_username="admin",
            )
            people.append(person)
        base_time = datetime(2026, 1, 1, tzinfo=UTC)
        for index, person in enumerate(people):
            await self.item_storage.touch_items(
                item_ids={person.item.id},
                author_username="admin",
                kind=KnowledgeItemKind.PERSON,
                updated_at=base_time + timedelta(days=index),
            )

        matching = await self.people_use_case.list_people(
            filters=PersonFilters(
                page=1,
                page_size=20,
                sort=PersonListSort.NAME_ASC,
                search_query="EXAMPLE.COM",
                tag_ids=(work.id, close.id),
                author_username="admin",
            ),
        )
        newest = await self.people_use_case.list_people(
            filters=PersonFilters(
                page=1,
                page_size=2,
                sort=PersonListSort.UPDATED_NEWEST,
                search_query=None,
                tag_ids=(),
                author_username="admin",
            ),
        )
        oldest = await self.people_use_case.list_people(
            filters=PersonFilters(
                page=1,
                page_size=3,
                sort=PersonListSort.UPDATED_OLDEST,
                search_query=None,
                tag_ids=(),
                author_username="admin",
            ),
        )
        descending = await self.people_use_case.list_people(
            filters=PersonFilters(
                page=2,
                page_size=2,
                sort=PersonListSort.NAME_DESC,
                search_query=None,
                tag_ids=(),
                author_username="admin",
            ),
        )

        assert [person.display_name for person in matching.values] == [
            "Альфа Анна",
            "Гамма Галина",
        ]
        assert matching.total_count == 2
        assert [person.display_name for person in newest.values] == [
            "Гамма Галина",
            "Бета Борис",
        ]
        assert [person.display_name for person in oldest.values] == [
            "Альфа Анна",
            "Бета Борис",
            "Гамма Галина",
        ]
        assert [person.display_name for person in descending.values] == ["Альфа Анна"]

        one_row_queries = await self.count_list_queries(page_size=1)
        three_row_queries = await self.count_list_queries(page_size=3)
        assert one_row_queries == three_row_queries == 6

    async def test_search_matches_names_and_email_but_not_phone_or_telegram(self) -> None:
        values = (
            ("Needle", "Name", "", "", ""),
            ("Email", "Match", "needle@example.com", "", ""),
            ("Phone", "Only", "", "+7-needle", ""),
            ("Telegram", "Only", "", "", "@needle"),
        )
        for last_name, first_name, email, phone, telegram in values:
            person = await self.people_use_case.create_person(
                params=PersonQuickCreateParams(
                    first_name=first_name,
                    last_name=last_name,
                    author_username="admin",
                ),
            )
            await self.people_use_case.update_person(
                person_id=person.item.id,
                params=person_update(
                    last_name=last_name,
                    first_name=first_name,
                    contacts=(email, phone, telegram),
                ),
                author_username="admin",
            )

        page = await self.people_use_case.list_people(
            filters=PersonFilters(
                page=1,
                page_size=20,
                sort=PersonListSort.NAME_ASC,
                search_query="needle",
                tag_ids=(),
                author_username="admin",
            ),
        )

        assert [person.display_name for person in page.values] == [
            "Email Match",
            "Needle Name",
        ]

    async def test_broad_search_keeps_runtime_binds_bounded_to_page_size(self) -> None:
        item_rows = [
            {
                "id": f"{index:032x}",
                "kind": KnowledgeItemKind.PERSON,
                "author_username": "admin",
                "display_name": f"Broadmatch Person {index}",
                "description": "",
            }
            for index in range(1, BROAD_MATCH_COUNT + 1)
        ]
        detail_rows = [
            {
                "item_id": f"{index:032x}",
                "author_username": "admin",
                "last_name": "Broadmatch",
                "first_name": f"Person {index}",
                "middle_name": "",
                "email": f"broadmatch-{index}@example.com",
                "phone": f"+7-broadmatch-{index}",
                "telegram": f"@broadmatch-{index}",
                "birthday_day": None,
                "birthday_month": None,
                "birthday_year": None,
            }
            for index in range(1, BROAD_MATCH_COUNT + 1)
        ]
        await self.db_session.execute(insert(KnowledgeItemModel), item_rows)
        await self.db_session.execute(insert(PersonDetailsModel), detail_rows)
        await self.db_session.flush()

        bind = self.db_session.get_bind()
        captured: list[tuple[str, int]] = []

        def record_statement(
            _connection: Connection,
            _cursor: object,
            statement: str,
            parameters: object,
            _context: object,
            _executemany: bool,
        ) -> None:
            parameter_count = len(parameters) if hasattr(parameters, "__len__") else 0
            captured.append((statement, parameter_count))

        event.listen(bind, "before_cursor_execute", record_statement)
        try:
            page = await self.people_use_case.list_people(
                filters=PersonFilters(
                    page=1,
                    page_size=20,
                    sort=PersonListSort.NAME_ASC,
                    search_query="broadmatch",
                    tag_ids=(),
                    author_username="admin",
                ),
            )
        finally:
            event.remove(bind, "before_cursor_execute", record_statement)

        assert page.total_count == BROAD_MATCH_COUNT
        assert len(page.values) == 20
        assert max(parameter_count for _, parameter_count in captured) <= 25
        assert any(
            "knowledge__person_details_model" in statement
            and "ORDER BY" in statement
            and "LIMIT" in statement
            for statement, _ in captured
        )

    async def test_used_tag_and_relationship_type_cannot_be_deleted(self) -> None:
        tag = await self.tags_use_case.create_tag(
            params=KnowledgeTagCreateParams(name="Работа", author_username="admin"),
        )
        relationship_type = await self.relationship_types_use_case.create_relationship_type(
            params=PersonRelationshipTypeCreateParams(
                author_username="admin",
                is_symmetric=True,
                forward_name="друг",
                reverse_name="",
            ),
        )
        source = await self.people_use_case.create_person(
            params=PersonQuickCreateParams(
                first_name="Иван",
                last_name="Иванов",
                author_username="admin",
            ),
        )
        target = await self.people_use_case.create_person(
            params=PersonQuickCreateParams(
                first_name="Пётр",
                last_name="Петров",
                author_username="admin",
            ),
        )
        await self.people_use_case.update_person(
            person_id=source.item.id,
            params=person_update(
                last_name="Иванов",
                first_name="Иван",
                tag_ids=[tag.id],
                relationship_changes=PersonRelationshipChanges(
                    create=[
                        PersonRelationshipCreateParams(
                            related_person_id=target.item.id,
                            relationship_type_id=relationship_type.id,
                            direction=PersonRelationshipDirection.FORWARD,
                            note="",
                        ),
                    ],
                    update=[],
                    delete_ids=[],
                ),
            ),
            author_username="admin",
        )

        with pytest.raises(KnowledgeConflictError):
            await self.tags_use_case.delete_tag(
                tag_id=tag.id,
                author_username="admin",
            )
        with pytest.raises(KnowledgeConflictError):
            await self.relationship_types_use_case.delete_relationship_type(
                relationship_type_id=relationship_type.id,
                author_username="admin",
            )

    async def test_relationship_batch_projects_both_sides_and_delete_cascades(self) -> None:
        directional = await self.relationship_types_use_case.create_relationship_type(
            params=PersonRelationshipTypeCreateParams(
                author_username="admin",
                is_symmetric=False,
                forward_name="руководитель",
                reverse_name="подчинённый",
            ),
        )
        symmetric = await self.relationship_types_use_case.create_relationship_type(
            params=PersonRelationshipTypeCreateParams(
                author_username="admin",
                is_symmetric=True,
                forward_name="друг",
                reverse_name="",
            ),
        )
        source, first, second, removed = [
            await self.people_use_case.create_person(
                params=PersonQuickCreateParams(
                    first_name=f"Имя{index}",
                    last_name=f"Фамилия{index}",
                    author_username="admin",
                ),
            )
            for index in range(4)
        ]
        initial = await self.people_use_case.update_person(
            person_id=source.item.id,
            params=person_update(
                last_name=source.details.last_name,
                first_name=source.details.first_name,
                relationship_changes=PersonRelationshipChanges(
                    create=[
                        PersonRelationshipCreateParams(
                            related_person_id=first.item.id,
                            relationship_type_id=directional.id,
                            direction=PersonRelationshipDirection.FORWARD,
                            note="первая",
                        ),
                        PersonRelationshipCreateParams(
                            related_person_id=removed.item.id,
                            relationship_type_id=symmetric.id,
                            direction=PersonRelationshipDirection.FORWARD,
                            note="удалить",
                        ),
                    ],
                    update=[],
                    delete_ids=[],
                ),
            ),
            author_username="admin",
        )
        directional_edge = next(
            value for value in initial.relationships if value.relationship_type.id == directional.id
        )
        removed_edge = next(
            value for value in initial.relationships if value.relationship_type.id == symmetric.id
        )

        updated = await self.people_use_case.update_person(
            person_id=source.item.id,
            params=person_update(
                last_name=source.details.last_name,
                first_name=source.details.first_name,
                relationship_changes=PersonRelationshipChanges(
                    create=[
                        PersonRelationshipCreateParams(
                            related_person_id=first.item.id,
                            relationship_type_id=symmetric.id,
                            direction=PersonRelationshipDirection.FORWARD,
                            note="дружба",
                        ),
                    ],
                    update=[
                        PersonRelationshipUpdateParams(
                            id=directional_edge.id,
                            related_person_id=second.item.id,
                            relationship_type_id=directional.id,
                            direction=PersonRelationshipDirection.FORWARD,
                            note="перенос",
                        ),
                    ],
                    delete_ids=[removed_edge.id],
                ),
            ),
            author_username="admin",
        )

        assert {(value.related_person_id, value.label) for value in updated.relationships} == {
            (first.item.id, "друг"),
            (second.item.id, "руководитель"),
        }
        first_view = await self.people_use_case.get_person(
            person_id=first.item.id,
            author_username="admin",
        )
        second_view = await self.people_use_case.get_person(
            person_id=second.item.id,
            author_username="admin",
        )
        removed_view = await self.people_use_case.get_person(
            person_id=removed.item.id,
            author_username="admin",
        )
        assert first_view.relationships[0].label == "друг"
        assert first_view.relationships[0].direction == PersonRelationshipDirection.REVERSE
        assert second_view.relationships[0].label == "подчинённый"
        assert second_view.relationships[0].direction == PersonRelationshipDirection.REVERSE
        assert removed_view.relationships == []

        await self.people_use_case.delete_person(
            person_id=source.item.id,
            author_username="admin",
        )

        assert (
            await self.people_use_case.get_person(
                person_id=first.item.id,
                author_username="admin",
            )
        ).relationships == []
        with pytest.raises(KnowledgeItemNotFoundError):
            await self.people_use_case.get_person(
                person_id=source.item.id,
                author_username="admin",
            )

    async def test_cross_author_relationship_is_rejected_as_not_found(self) -> None:
        own = await self.people_use_case.create_person(
            params=PersonQuickCreateParams(
                first_name="Иван",
                last_name="Иванов",
                author_username="admin",
            ),
        )
        foreign = await self.people_use_case.create_person(
            params=PersonQuickCreateParams(
                first_name="Пётр",
                last_name="Петров",
                author_username="other-admin",
            ),
        )
        relationship_type = await self.relationship_types_use_case.create_relationship_type(
            params=PersonRelationshipTypeCreateParams(
                author_username="admin",
                is_symmetric=True,
                forward_name="друг",
                reverse_name="",
            ),
        )

        with pytest.raises(PersonRelationshipNotFoundError):
            await self.people_use_case.update_person(
                person_id=own.item.id,
                params=person_update(
                    last_name="Иванов",
                    first_name="Иван",
                    relationship_changes=PersonRelationshipChanges(
                        create=[
                            PersonRelationshipCreateParams(
                                related_person_id=foreign.item.id,
                                relationship_type_id=relationship_type.id,
                                direction=PersonRelationshipDirection.FORWARD,
                                note="",
                            ),
                        ],
                        update=[],
                        delete_ids=[],
                    ),
                ),
                author_username="admin",
            )

    async def test_private_file_metadata_is_author_scoped_and_cascades_with_person(
        self,
    ) -> None:
        person = await self.people_use_case.create_person(
            params=PersonQuickCreateParams(
                first_name="Иван",
                last_name="Иванов",
                author_username="admin",
            ),
        )
        now = datetime.now(tz=UTC)
        file = await self.file_storage.create_file(
            file=KnowledgeFile(
                id="f" * 32,
                item_id=person.item.id,
                author_username="admin",
                kind=KnowledgeFileKind.ATTACHMENT,
                relative_path="attachments/private.txt",
                mime_type="text/plain",
                size_bytes=7,
                name="Private",
                original_name="private.txt",
                original_sha256="a" * 64,
                created_at=now,
                updated_at=now,
            ),
        )

        assert (
            await self.file_storage.get_file(
                file_id=file.id,
                author_username="admin",
            )
        ).item_id == person.item.id
        with pytest.raises(KnowledgeFileNotFoundError):
            await self.file_storage.get_file(
                file_id=file.id,
                author_username="other-admin",
            )

        object_names = await self.people_use_case.delete_person(
            person_id=person.item.id,
            author_username="admin",
        )

        assert object_names == ("attachments/private.txt",)
        with pytest.raises(KnowledgeFileNotFoundError):
            await self.file_storage.get_file(
                file_id=file.id,
                author_username="admin",
            )

    async def count_list_queries(self, *, page_size: int) -> int:
        bind = self.db_session.get_bind()
        statements: list[str] = []

        def record_statement(
            _connection: Connection,
            _cursor: object,
            statement: str,
            _parameters: object,
            _context: object,
            _executemany: bool,
        ) -> None:
            statements.append(statement)

        event.listen(bind, "before_cursor_execute", record_statement)
        try:
            await self.people_use_case.list_people(
                filters=PersonFilters(
                    page=1,
                    page_size=page_size,
                    sort=PersonListSort.NAME_ASC,
                    search_query=None,
                    tag_ids=(),
                    author_username="admin",
                ),
            )
        finally:
            event.remove(bind, "before_cursor_execute", record_statement)
        return len(statements)
