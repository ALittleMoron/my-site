from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from core.knowledge.exceptions import (
    InvalidKnowledgeDataError,
    KnowledgeConflictError,
    KnowledgeTagNotFoundError,
    PersonRelationshipNotFoundError,
    PersonRelationshipTypeNotFoundError,
)
from core.knowledge.files.storages import KnowledgeFilesStorage
from core.knowledge.items.enums import KnowledgeItemKind
from core.knowledge.items.schemas import (
    KnowledgeItem,
    KnowledgeTag,
)
from core.knowledge.items.services import KnowledgeItemCrudService
from core.knowledge.items.storages import KnowledgeItemsStorage
from core.knowledge.people.enums import (
    PersonListSort,
    PersonRelationshipDirection,
)
from core.knowledge.people.schemas import (
    PersonDetails,
    PersonFilters,
    PersonRelationship,
    PersonRelationshipChanges,
    PersonRelationshipCreateParams,
    PersonRelationshipType,
    PersonRelationshipUpdateParams,
    PersonUpdateParams,
)
from core.knowledge.people.storages import PeopleStorage
from core.knowledge.people.use_cases import PeopleUseCase
from tests.test_cases import TestCase

CURRENT_DATETIME = datetime(2026, 7, 27, 12, 0, tzinfo=UTC)


def knowledge_item(
    *,
    item_id: str,
    display_name: str,
    author_username: str = "owner",
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        kind=KnowledgeItemKind.PERSON,
        author_username=author_username,
        display_name=display_name,
        description="",
        tags=[],
        created_at=CURRENT_DATETIME,
        updated_at=CURRENT_DATETIME,
    )


def person_details(
    *,
    item_id: str,
    last_name: str = "Иванов",
    telegram: str = "",
) -> PersonDetails:
    return PersonDetails(
        item_id=item_id,
        last_name=last_name,
        first_name="Иван",
        middle_name="",
        email="",
        phone="",
        telegram=telegram,
        birthday=None,
    )


def relationship_type(*, relationship_type_id: str) -> PersonRelationshipType:
    return PersonRelationshipType(
        id=relationship_type_id,
        author_username="owner",
        is_symmetric=False,
        forward_name="руководитель",
        reverse_name="подчинённый",
        created_at=CURRENT_DATETIME,
        updated_at=CURRENT_DATETIME,
    )


def relationship(
    *,
    relationship_id: str,
    source_person_id: str,
    target_person_id: str,
    type_schema: PersonRelationshipType,
) -> PersonRelationship:
    return PersonRelationship(
        id=relationship_id,
        author_username="owner",
        source_person_id=source_person_id,
        target_person_id=target_person_id,
        relationship_type=type_schema,
        note="",
        created_at=CURRENT_DATETIME,
        updated_at=CURRENT_DATETIME,
    )


class TestKnowledgeItemCrudService(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=KnowledgeItemsStorage)
        self.service = KnowledgeItemCrudService(storage=self.storage)

    async def test_update_item_replaces_tags_after_typed_item_update(self) -> None:
        item = knowledge_item(
            item_id=self.factory.core.hex_id(1),
            display_name="Иванов Иван",
        )
        tag = KnowledgeTag(
            id=self.factory.core.hex_id(2),
            author_username="owner",
            name="Работа",
            created_at=CURRENT_DATETIME,
            updated_at=CURRENT_DATETIME,
        )
        self.storage.get_tags_by_ids.return_value = [tag]
        self.storage.update_item.return_value = item

        updated = await self.service.update_item(
            item=item,
            params=Mock(),
            tag_ids=[tag.id],
            updated_at=CURRENT_DATETIME,
        )

        assert updated == item
        self.storage.replace_item_tags.assert_awaited_once_with(
            item_id=item.id,
            author_username="owner",
            tag_ids=[tag.id],
        )


class TestPeopleUseCase(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.item_service = Mock(spec=KnowledgeItemCrudService)
        self.item_storage = Mock(spec=KnowledgeItemsStorage)
        self.people_storage = Mock(spec=PeopleStorage)
        self.file_storage = Mock(spec=KnowledgeFilesStorage)
        self.file_storage.list_files_for_items.return_value = []
        self.file_storage.list_item_files.return_value = []
        self.use_case = PeopleUseCase(
            item_service=self.item_service,
            item_storage=self.item_storage,
            people_storage=self.people_storage,
            file_storage=self.file_storage,
        )

    async def test_list_validates_tags_then_fetches_and_reorders_only_page_items(self) -> None:
        first_id = self.factory.core.hex_id(1)
        second_id = self.factory.core.hex_id(2)
        tag_id = self.factory.core.hex_id(3)
        tag = KnowledgeTag(
            id=tag_id,
            author_username="owner",
            name="Work",
            created_at=CURRENT_DATETIME,
            updated_at=CURRENT_DATETIME,
        )
        first_item = knowledge_item(item_id=first_id, display_name="Alpha")
        second_item = knowledge_item(item_id=second_id, display_name="Beta")
        self.item_storage.get_tags_by_ids.return_value = [tag]
        self.people_storage.list_person_page.return_value = ([second_id, first_id], 2)
        self.item_storage.get_items_by_ids.return_value = [first_item, second_item]
        self.people_storage.list_details.return_value = [
            person_details(item_id=first_id, last_name="Alpha"),
            person_details(item_id=second_id, last_name="Beta", telegram="@beta"),
        ]
        filters = PersonFilters(
            page=2,
            page_size=50,
            sort=PersonListSort.NAME_DESC,
            search_query="  example.com  ",
            tag_ids=(tag_id,),
            author_username="owner",
        )

        page = await self.use_case.list_people(filters=filters)

        assert [person.id for person in page.values] == [second_id, first_id]
        assert page.values[0].telegram == "@beta"
        assert page.total_count == 2
        self.item_storage.get_tags_by_ids.assert_awaited_once_with(
            tag_ids={tag_id},
            author_username="owner",
        )
        self.people_storage.list_person_page.assert_awaited_once_with(
            filters=PersonFilters(
                page=2,
                page_size=50,
                sort=PersonListSort.NAME_DESC,
                search_query="example.com",
                tag_ids=(tag_id,),
                author_username="owner",
            ),
        )
        self.item_storage.get_items_by_ids.assert_awaited_once_with(
            item_ids={first_id, second_id},
            author_username="owner",
            kind=KnowledgeItemKind.PERSON,
        )

    async def test_list_rejects_tag_not_owned_by_author_before_page_query(self) -> None:
        tag_id = self.factory.core.hex_id(1)
        self.item_storage.get_tags_by_ids.return_value = []
        filters = PersonFilters(
            page=1,
            page_size=20,
            sort=PersonListSort.UPDATED_NEWEST,
            search_query=None,
            tag_ids=(tag_id,),
            author_username="owner",
        )

        with pytest.raises(KnowledgeTagNotFoundError):
            await self.use_case.list_people(filters=filters)

        self.people_storage.list_person_page.assert_not_called()
        self.item_storage.get_items_by_ids.assert_not_called()

    async def test_update_relationship_touches_old_and_new_related_people(self) -> None:
        person_id = self.factory.core.hex_id(1)
        old_related_id = self.factory.core.hex_id(2)
        new_related_id = self.factory.core.hex_id(3)
        relationship_id = self.factory.core.hex_id(4)
        relationship_type_id = self.factory.core.hex_id(5)
        item = knowledge_item(item_id=person_id, display_name="Иванов Иван")
        new_related_item = knowledge_item(
            item_id=new_related_id,
            display_name="Петров Пётр",
        )
        type_schema = relationship_type(relationship_type_id=relationship_type_id)
        old_relationship = relationship(
            relationship_id=relationship_id,
            source_person_id=person_id,
            target_person_id=old_related_id,
            type_schema=type_schema,
        )
        self.item_service.get_item.return_value = item
        self.people_storage.get_details.return_value = person_details(item_id=person_id)
        self.people_storage.get_relationships_by_ids.return_value = [old_relationship]
        self.people_storage.get_relationship_types_by_ids.return_value = [type_schema]
        self.item_storage.get_items_by_ids.side_effect = [[new_related_item], []]
        self.people_storage.list_relationships.return_value = []
        params = PersonUpdateParams(
            last_name="Иванов",
            first_name="Иван",
            middle_name="",
            email="",
            phone="",
            telegram="",
            birthday=None,
            description="",
            tag_ids=[],
            relationship_changes=PersonRelationshipChanges(
                create=[],
                update=[
                    PersonRelationshipUpdateParams(
                        id=relationship_id,
                        related_person_id=new_related_id,
                        relationship_type_id=relationship_type_id,
                        direction=PersonRelationshipDirection.FORWARD,
                        note="перенесено",
                    ),
                ],
                delete_ids=[],
            ),
        )

        await self.use_case.update_person(
            person_id=person_id,
            params=params,
            author_username="owner",
        )

        touch_call = self.item_storage.touch_items.await_args
        assert touch_call.kwargs["item_ids"] == {old_related_id, new_related_id}
        self.people_storage.update_relationships.assert_awaited_once()

    async def test_validate_relationship_changes_rejects_self_link(self) -> None:
        person_id = self.factory.core.hex_id(1)
        changes = PersonRelationshipChanges(
            create=[
                PersonRelationshipCreateParams(
                    related_person_id=person_id,
                    relationship_type_id=self.factory.core.hex_id(2),
                    direction=PersonRelationshipDirection.FORWARD,
                    note="",
                ),
            ],
            update=[],
            delete_ids=[],
        )
        self.people_storage.get_relationships_by_ids.return_value = []

        with pytest.raises(InvalidKnowledgeDataError):
            await self.use_case.validate_relationship_changes(
                person_id=person_id,
                changes=changes,
                author_username="owner",
            )

    async def test_validate_relationship_changes_rejects_foreign_person_or_type(self) -> None:
        person_id = self.factory.core.hex_id(1)
        changes = PersonRelationshipChanges(
            create=[
                PersonRelationshipCreateParams(
                    related_person_id=self.factory.core.hex_id(2),
                    relationship_type_id=self.factory.core.hex_id(3),
                    direction=PersonRelationshipDirection.FORWARD,
                    note="",
                ),
            ],
            update=[],
            delete_ids=[],
        )
        self.people_storage.get_relationships_by_ids.return_value = []
        self.item_storage.get_items_by_ids.return_value = []

        with pytest.raises(PersonRelationshipNotFoundError):
            await self.use_case.validate_relationship_changes(
                person_id=person_id,
                changes=changes,
                author_username="owner",
            )

        self.item_storage.get_items_by_ids.return_value = [
            knowledge_item(
                item_id=self.factory.core.hex_id(2),
                display_name="Петров Пётр",
            ),
        ]
        self.people_storage.get_relationship_types_by_ids.return_value = []

        with pytest.raises(PersonRelationshipTypeNotFoundError):
            await self.use_case.validate_relationship_changes(
                person_id=person_id,
                changes=changes,
                author_username="owner",
            )

    async def test_validate_relationship_changes_rejects_duplicate_pair_and_type(self) -> None:
        person_id = self.factory.core.hex_id(1)
        related_id = self.factory.core.hex_id(2)
        relationship_type_id = self.factory.core.hex_id(3)
        create = PersonRelationshipCreateParams(
            related_person_id=related_id,
            relationship_type_id=relationship_type_id,
            direction=PersonRelationshipDirection.FORWARD,
            note="",
        )
        changes = PersonRelationshipChanges(
            create=[create, create],
            update=[],
            delete_ids=[],
        )
        self.people_storage.get_relationships_by_ids.return_value = []
        self.item_storage.get_items_by_ids.return_value = [
            knowledge_item(item_id=related_id, display_name="Петров Пётр"),
        ]
        self.people_storage.get_relationship_types_by_ids.return_value = [
            relationship_type(relationship_type_id=relationship_type_id),
        ]

        with pytest.raises(KnowledgeConflictError):
            await self.use_case.validate_relationship_changes(
                person_id=person_id,
                changes=changes,
                author_username="owner",
            )
