from datetime import UTC, datetime

import pytest
import pytest_asyncio
from httpx import codes

from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser
from core.knowledge.exceptions import KnowledgeConflictError, KnowledgeItemNotFoundError
from core.knowledge.items.enums import KnowledgeItemKind
from core.knowledge.items.schemas import KnowledgeItem, KnowledgeTag
from core.knowledge.people.enums import PersonListSort
from core.knowledge.people.schemas import (
    PeoplePage,
    Person,
    PersonDetails,
    PersonFilters,
    PersonQuickCreateParams,
    PersonUpdateParams,
)
from entrypoints.litestar.api.knowledge.items.endpoints import AdminKnowledgeTagsApiController
from entrypoints.litestar.api.knowledge.people.endpoints import AdminPeopleApiController
from entrypoints.litestar.guards import team_manager_guard
from tests.test_cases import ApiTestCase

CURRENT_DATETIME = datetime(2026, 7, 27, 12, 0, tzinfo=UTC)


def person_response(*, person_id: str = "1" * 32) -> Person:
    item = KnowledgeItem(
        id=person_id,
        kind=KnowledgeItemKind.PERSON,
        author_username="test",
        display_name="Иванов Иван",
        description="",
        tags=[],
        created_at=CURRENT_DATETIME,
        updated_at=CURRENT_DATETIME,
    )
    return Person(
        item=item,
        details=PersonDetails(
            item_id=person_id,
            last_name="Иванов",
            first_name="Иван",
            middle_name="",
            email="",
            phone="",
            telegram="",
            birthday=None,
        ),
        relationships=[],
        related_dates=[],
        photo=None,
        attachments=[],
    )


def person_update_payload() -> dict[str, object]:
    return {
        "lastName": "Иванов",
        "firstName": "Иван",
        "middleName": "",
        "email": "",
        "phone": "",
        "telegram": "",
        "birthday": None,
        "description": "",
        "tagIds": [],
        "relationshipChanges": {
            "create": [],
            "update": [],
            "deleteIds": [],
        },
    }


class TestPeopleApi(ApiTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.people_use_case = await self.container.get_people_use_case()
        self.tags_use_case = await self.container.get_knowledge_tags_use_case()
        self.relationship_types_use_case = (
            await self.container.get_person_relationship_types_use_case()
        )

    def test_list_requires_explicit_pagination_and_sort(self) -> None:
        for response in (
            self.api.get_admin_people(page=None),
            self.api.get_admin_people(page_size=None),
            self.api.get_admin_people(sort=None),
        ):
            self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.people_use_case.list_people.assert_not_called()

    def test_list_maps_filters_and_returns_lightweight_page(self) -> None:
        self.people_use_case.list_people.return_value = PeoplePage(
            values=[],
            total_count=0,
            total_pages=0,
        )

        response = self.api.get_admin_people(
            page=2,
            page_size=50,
            sort="nameDesc",
            search_query="  Иван  ",
            tag_ids=["1" * 32, "2" * 32, "1" * 32],
        )

        self.asserts.status(response=response, expected_status=codes.OK)
        assert response.headers["cache-control"] == "no-store"
        assert response.json() == {"totalCount": 0, "totalPages": 0, "people": []}
        self.people_use_case.list_people.assert_called_once_with(
            filters=PersonFilters(
                page=2,
                page_size=50,
                sort=PersonListSort.NAME_DESC,
                search_query="Иван",
                tag_ids=("1" * 32, "2" * 32),
                author_username="test",
            ),
        )

    def test_list_normalizes_blank_search_to_absent_filter(self) -> None:
        self.people_use_case.list_people.return_value = PeoplePage(
            values=[],
            total_count=0,
            total_pages=0,
        )

        response = self.api.get_admin_people(search_query="   ")

        self.asserts.status(response=response, expected_status=codes.OK)
        self.people_use_case.list_people.assert_called_once_with(
            filters=PersonFilters(
                page=1,
                page_size=20,
                sort=PersonListSort.UPDATED_NEWEST,
                search_query=None,
                tag_ids=(),
                author_username="test",
            ),
        )

    def test_quick_create_requires_both_names_and_returns_blankable_fields(self) -> None:
        self.people_use_case.create_person.return_value = person_response()

        response = self.api.post_admin_person(
            data={"firstName": "Иван", "lastName": "Иванов"},
        )

        self.asserts.status(response=response, expected_status=codes.CREATED)
        assert response.json()["middleName"] == ""
        assert response.json()["email"] == ""
        assert response.json()["phone"] == ""
        assert response.json()["telegram"] == ""
        assert response.json()["description"] == ""
        assert response.json()["birthday"] is None
        self.people_use_case.create_person.assert_called_once_with(
            params=PersonQuickCreateParams(
                first_name="Иван",
                last_name="Иванов",
                author_username="test",
            ),
        )

        for payload in (
            {"lastName": "Иванов"},
            {"firstName": "Иван"},
            {"firstName": "   ", "lastName": "Иванов"},
        ):
            invalid_response = self.api.post_admin_person(data=payload)
            self.asserts.status(
                response=invalid_response,
                expected_status=codes.BAD_REQUEST,
            )

    @pytest.mark.parametrize(
        ("birthday", "expected_status"),
        [
            (None, codes.OK),
            ({"day": 29, "month": 2, "year": None}, codes.OK),
            ({"day": 29, "month": 2, "year": 2024}, codes.OK),
            ({"day": 31, "month": 4, "year": None}, codes.BAD_REQUEST),
            ({"day": 29, "month": 2, "year": 2025}, codes.BAD_REQUEST),
            ({"day": 28, "month": 7, "year": 2027}, codes.BAD_REQUEST),
        ],
    )
    def test_update_validates_birthday(
        self,
        birthday: dict[str, int | None] | None,
        expected_status: int,
    ) -> None:
        self.people_use_case.update_person.return_value = person_response()
        payload = person_update_payload()
        payload["birthday"] = birthday

        response = self.api.put_admin_person(person_id=1, data=payload)

        self.asserts.status(response=response, expected_status=expected_status)
        if expected_status == codes.OK:
            self.people_use_case.update_person.assert_called()

    def test_update_maps_explicit_relationship_batch(self) -> None:
        self.people_use_case.update_person.return_value = person_response()
        payload = person_update_payload()
        payload["relationshipChanges"] = {
            "create": [
                {
                    "relatedPersonId": "2" * 32,
                    "relationshipTypeId": "3" * 32,
                    "direction": "forward",
                    "note": "",
                },
            ],
            "update": [],
            "deleteIds": ["4" * 32],
        }

        response = self.api.put_admin_person(person_id=1, data=payload)

        self.asserts.status(response=response, expected_status=codes.OK)
        call = self.people_use_case.update_person.call_args
        assert call.kwargs["person_id"] == "0" * 31 + "1"
        assert call.kwargs["author_username"] == "test"
        params = call.kwargs["params"]
        assert isinstance(params, PersonUpdateParams)
        assert params.telegram == ""
        assert params.relationship_changes.delete_ids == ["4" * 32]
        assert params.relationship_changes.create[0].related_person_id == "2" * 32
        assert call.kwargs["current_datetime"].tzinfo is not None

    def test_delete_person_forwards_request_datetime(self) -> None:
        self.people_use_case.delete_person.return_value = ()

        response = self.api.delete_admin_person(person_id=1)

        self.asserts.status(response=response, expected_status=codes.NO_CONTENT)
        assert (
            self.people_use_case.delete_person.await_args.kwargs["current_datetime"].tzinfo
            is not None
        )

    def test_update_tag_forwards_request_datetime(self) -> None:
        tag = KnowledgeTag(
            id="1" * 32,
            author_username="test",
            name="Career",
            created_at=CURRENT_DATETIME,
            updated_at=CURRENT_DATETIME,
        )
        self.tags_use_case.update_tag.return_value = tag

        response = self.api.put_admin_knowledge_tag(tag_id=1, data={"name": "Career"})

        self.asserts.status(response=response, expected_status=codes.OK)
        current_datetime = self.tags_use_case.update_tag.await_args.kwargs["current_datetime"]
        assert current_datetime.tzinfo is not None

    def test_update_rejects_telegram_longer_than_storage_contract(self) -> None:
        payload = person_update_payload()
        payload["telegram"] = "t" * 256

        response = self.api.put_admin_person(person_id=1, data=payload)

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.people_use_case.update_person.assert_not_called()

    def test_update_requires_telegram_field(self) -> None:
        payload = person_update_payload()
        del payload["telegram"]

        response = self.api.put_admin_person(person_id=1, data=payload)

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.people_use_case.update_person.assert_not_called()

    def test_foreign_or_missing_person_is_exposed_as_same_not_found(self) -> None:
        self.people_use_case.get_person.side_effect = KnowledgeItemNotFoundError()

        response = self.api.get_admin_person(person_id=404)

        self.asserts.error_message(
            response=response,
            expected_status=codes.NOT_FOUND,
            expected_message=KnowledgeItemNotFoundError.message,
        )
        self.people_use_case.get_person.assert_called_once_with(
            person_id=self.factory.core.hex_id(404),
            author_username="test",
        )

    def test_used_tag_and_relationship_type_return_conflict(self) -> None:
        self.tags_use_case.delete_tag.side_effect = KnowledgeConflictError()
        self.relationship_types_use_case.delete_relationship_type.side_effect = (
            KnowledgeConflictError()
        )

        tag_response = self.api.delete_admin_knowledge_tag(tag_id=1)
        type_response = self.api.delete_admin_person_relationship_type(
            relationship_type_id=2,
        )

        self.asserts.error_message(
            response=tag_response,
            expected_status=codes.CONFLICT,
            expected_message=KnowledgeConflictError.message,
        )
        self.asserts.error_message(
            response=type_response,
            expected_status=codes.CONFLICT,
            expected_message=KnowledgeConflictError.message,
        )


class TestPeopleTeamManagerAccess(ApiTestCase):
    @pytest.fixture(params=[RoleEnum.OWNER, RoleEnum.ADMIN])
    def jwt_admin(self, request: pytest.FixtureRequest) -> JwtUser:
        return JwtUser(username=request.param.value, role=request.param)

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        use_case = await self.container.get_people_use_case()
        use_case.list_people.return_value = PeoplePage(
            values=[],
            total_count=0,
            total_pages=0,
        )

    def test_owner_and_admin_can_list_people(self) -> None:
        response = self.api.get_admin_people()

        self.asserts.status(response=response, expected_status=codes.OK)


class TestPeopleNonTeamManagerAccess(ApiTestCase):
    @pytest.fixture(params=[RoleEnum.MODERATOR, RoleEnum.USER])
    def jwt_admin(self, request: pytest.FixtureRequest) -> JwtUser:
        return JwtUser(username=request.param.value, role=request.param)

    def test_moderator_and_user_cannot_access_people(self) -> None:
        response = self.api.get_admin_people()

        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)


class TestAnonymousPeopleAccess(ApiTestCase):
    def test_anonymous_cannot_access_people(self) -> None:
        response = self.no_auth_api.get_admin_people()

        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)


class TestPeopleRouteMetadata(ApiTestCase):
    def test_controllers_use_team_manager_guard(self) -> None:
        assert AdminPeopleApiController.guards == [team_manager_guard]
        assert AdminKnowledgeTagsApiController.guards == [team_manager_guard]

    def test_private_get_handlers_are_not_cached(self) -> None:
        assert AdminPeopleApiController.list_people.cache is False
        assert AdminPeopleApiController.get_person.cache is False
        assert AdminPeopleApiController.list_relationship_types.cache is False
        assert AdminKnowledgeTagsApiController.list_tags.cache is False

    def test_relationship_changes_schema_requires_all_explicit_lists(self) -> None:
        payload = person_update_payload()
        payload["relationshipChanges"] = {"create": [], "update": []}

        response = self.api.put_admin_person(person_id=1, data=payload)

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
