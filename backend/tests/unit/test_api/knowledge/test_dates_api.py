from datetime import UTC, datetime

import pytest
import pytest_asyncio
from httpx import codes

from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser
from core.knowledge.dates.enums import KnowledgeDateListSort
from core.knowledge.dates.schemas import (
    KnowledgeDate,
    KnowledgeDateCreateParams,
    KnowledgeDateDetails,
    KnowledgeDateFilters,
    KnowledgeDatesPage,
    KnowledgeDateUpdateParams,
    KnowledgeDateValue,
)
from core.knowledge.items.enums import KnowledgeItemKind
from core.knowledge.items.schemas import KnowledgeItem
from entrypoints.litestar.api.knowledge.dates.endpoints import (
    AdminKnowledgeDatesApiController,
)
from entrypoints.litestar.guards import team_manager_guard
from tests.test_cases import ApiTestCase

CURRENT_DATETIME = datetime(2026, 7, 30, 12, 0, tzinfo=UTC)


def date_response(*, date_id: str = "1" * 32) -> KnowledgeDate:
    return KnowledgeDate(
        item=KnowledgeItem(
            id=date_id,
            kind=KnowledgeItemKind.DATE,
            author_username="test",
            display_name="Годовщина",
            description="",
            tags=[],
            created_at=CURRENT_DATETIME,
            updated_at=CURRENT_DATETIME,
        ),
        details=KnowledgeDateDetails(
            item_id=date_id,
            date=KnowledgeDateValue(day=29, month=2, year=None),
        ),
        related_people=[],
        attachments=[],
    )


def update_payload() -> dict[str, object]:
    return {
        "displayName": "Годовщина",
        "date": {"day": 29, "month": 2, "year": None},
        "description": "",
        "tagIds": [],
        "personIds": [],
    }


class TestKnowledgeDatesApi(ApiTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_knowledge_dates_use_case()

    def test_list_requires_pagination_sort_and_maps_all_filters(self) -> None:
        for response in (
            self.api.get_admin_knowledge_dates(page=None),
            self.api.get_admin_knowledge_dates(page_size=None),
            self.api.get_admin_knowledge_dates(sort=None),
        ):
            self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.list_dates.assert_not_called()
        self.use_case.list_dates.return_value = KnowledgeDatesPage(
            values=[],
            total_count=0,
            total_pages=0,
        )

        response = self.api.get_admin_knowledge_dates(
            page=2,
            page_size=50,
            sort="dateDesc",
            search_query="  годов  ",
            tag_ids=["1" * 32, "1" * 32, "2" * 32],
            related_person_id="3" * 32,
        )

        self.asserts.status(response=response, expected_status=codes.OK)
        assert response.headers["cache-control"] == "no-store"
        assert response.json() == {"totalCount": 0, "totalPages": 0, "dates": []}
        self.use_case.list_dates.assert_called_once_with(
            filters=KnowledgeDateFilters(
                page=2,
                page_size=50,
                sort=KnowledgeDateListSort.DATE_DESC,
                search_query="годов",
                tag_ids=("1" * 32, "2" * 32),
                related_person_id="3" * 32,
                author_username="test",
            ),
        )

    @pytest.mark.parametrize(
        ("date_value", "expected_status"),
        [
            ({"day": 29, "month": 2, "year": None}, codes.CREATED),
            ({"day": 29, "month": 2, "year": 2024}, codes.CREATED),
            ({"day": 31, "month": 4, "year": None}, codes.BAD_REQUEST),
            ({"day": 29, "month": 2, "year": 2025}, codes.BAD_REQUEST),
            ({"day": 31, "month": 7, "year": 2027}, codes.BAD_REQUEST),
        ],
    )
    def test_create_validates_calendar_date(
        self,
        date_value: dict[str, int | None],
        expected_status: int,
    ) -> None:
        self.use_case.create_date.return_value = date_response()

        response = self.api.post_admin_knowledge_date(
            data={"displayName": "Годовщина", "date": date_value},
        )

        self.asserts.status(response=response, expected_status=expected_status)
        if expected_status == codes.CREATED:
            assert response.json()["date"]["day"] == 29

    def test_create_maps_required_fields(self) -> None:
        self.use_case.create_date.return_value = date_response()

        response = self.api.post_admin_knowledge_date(
            data={
                "displayName": "Годовщина",
                "date": {"day": 29, "month": 2, "year": None},
            },
        )

        self.asserts.status(response=response, expected_status=codes.CREATED)
        call = self.use_case.create_date.call_args
        assert call.kwargs["params"] == KnowledgeDateCreateParams(
            display_name="Годовщина",
            date=KnowledgeDateValue(day=29, month=2, year=None),
            author_username="test",
        )
        assert call.kwargs["today"].year >= 2026

    def test_update_maps_people_tags_and_rejects_duplicate_people(self) -> None:
        self.use_case.update_date.return_value = date_response()
        payload = update_payload()
        payload["tagIds"] = ["2" * 32]
        payload["personIds"] = ["3" * 32]

        response = self.api.put_admin_knowledge_date(date_id=1, data=payload)

        self.asserts.status(response=response, expected_status=codes.OK)
        call = self.use_case.update_date.call_args
        assert call.kwargs["date_id"] == "0" * 31 + "1"
        assert call.kwargs["params"] == KnowledgeDateUpdateParams(
            display_name="Годовщина",
            date=KnowledgeDateValue(day=29, month=2, year=None),
            description="",
            tag_ids=["2" * 32],
            person_ids=["3" * 32],
        )
        assert call.kwargs["author_username"] == "test"
        assert call.kwargs["current_datetime"].tzinfo is not None

        payload["personIds"] = ["3" * 32, "3" * 32]
        duplicate_response = self.api.put_admin_knowledge_date(date_id=1, data=payload)
        self.asserts.status(response=duplicate_response, expected_status=codes.BAD_REQUEST)

    def test_controller_is_admin_scoped_and_uncached(self) -> None:
        assert AdminKnowledgeDatesApiController.guards == [team_manager_guard]
        assert AdminKnowledgeDatesApiController.list_dates.cache is False
        assert AdminKnowledgeDatesApiController.get_date.cache is False


class TestKnowledgeDatesTeamManagerAccess(ApiTestCase):
    @pytest.fixture(params=[RoleEnum.OWNER, RoleEnum.ADMIN])
    def jwt_admin(self, request: pytest.FixtureRequest) -> JwtUser:
        return JwtUser(username=request.param.value, role=request.param)

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        use_case = await self.container.get_knowledge_dates_use_case()
        use_case.list_dates.return_value = KnowledgeDatesPage(
            values=[],
            total_count=0,
            total_pages=0,
        )

    def test_owner_and_admin_can_list_dates(self) -> None:
        response = self.api.get_admin_knowledge_dates()
        self.asserts.status(response=response, expected_status=codes.OK)


class TestKnowledgeDatesDeniedAccess(ApiTestCase):
    @pytest.fixture(params=[RoleEnum.MODERATOR, RoleEnum.USER])
    def jwt_admin(self, request: pytest.FixtureRequest) -> JwtUser:
        return JwtUser(username=request.param.value, role=request.param)

    def test_non_team_managers_cannot_list_dates(self) -> None:
        response = self.api.get_admin_knowledge_dates()
        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)


class TestAnonymousKnowledgeDatesAccess(ApiTestCase):
    def test_anonymous_cannot_list_dates(self) -> None:
        response = self.no_auth_api.get_admin_knowledge_dates()
        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)
