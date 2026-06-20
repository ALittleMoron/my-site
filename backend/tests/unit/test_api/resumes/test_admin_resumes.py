import pytest_asyncio
from httpx import codes

from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser
from core.i18n.enums import LanguageEnum
from core.resumes.enums import ResumeCurrentStatusEnum
from core.resumes.exceptions import ResumeNotFoundError
from core.resumes.schemas import (
    ResumeCreateParams,
    ResumeExperienceItem,
    ResumeFilters,
    ResumeProjectItem,
    ResumeUpdateParams,
)
from core.types import IntId
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestAdminResumesAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.authentication_use_case = await self.container.get_auth_use_case()
        self.use_case = await self.container.get_resumes_use_case()

    def test_list_resumes(self) -> None:
        resume = self.factory.core.resume(
            resume_id=1,
            title="Backend resume",
            created_at="2026-01-01T03:04:05",
            updated_at="2026-01-02T03:04:05",
        )
        self.use_case.list_resumes.return_value = self.factory.core.resumes(
            values=[resume],
            total_count=1,
            total_pages=1,
        )

        response = self.api.get_admin_resumes(page=2, page_size=10)

        assert response.status_code == codes.OK, response.content
        assert response.json()["totalCount"] == 1
        assert response.json()["totalPages"] == 1
        assert response.json()["resumes"][0]["id"] == 1
        assert response.json()["resumes"][0]["title"] == "Backend resume"
        assert response.json()["resumes"][0]["language"] == "ru"
        assert response.json()["resumes"][0]["content"]["profile"]["fullName"] == "Candidate Name"
        assert response.json()["resumes"][0]["content"]["profile"]["phone"] == ""
        assert response_has_no_resume_localized_field_names(value=response.json()["resumes"][0])
        assert_resume_response_nulls_are_dates_only(value=response.json()["resumes"][0]["content"])
        self.use_case.list_resumes.assert_called_once_with(
            filters=ResumeFilters(
                page=2,
                page_size=10,
                search_query=None,
                author_username="test",
            ),
        )

    def test_create_resume_maps_payload_to_params(self) -> None:
        experience = [
            ResumeExperienceItem(
                company="Company",
                position="Engineer",
                location="",
                start_date=None,
                end_date=None,
                current_status=ResumeCurrentStatusEnum.CURRENT,
                summary="Built a platform.",
                highlights=["Reduced latency"],
                technologies=["Python"],
                projects=[
                    ResumeProjectItem(
                        name="Portfolio",
                        role="Creator",
                        description="Site and knowledge base",
                        highlights=["Hybrid SSR/CSR"],
                        technologies=["Litestar", "Angular"],
                        url="https://example.com",
                    ),
                ],
            ),
        ]
        api_experience = [
            {
                "company": "Company",
                "position": "Engineer",
                "location": "",
                "startDate": None,
                "endDate": None,
                "currentStatus": "current",
                "summary": "Built a platform.",
                "highlights": ["Reduced latency"],
                "technologies": ["Python"],
                "projects": [
                    {
                        "name": "Portfolio",
                        "role": "Creator",
                        "description": "Site and knowledge base",
                        "highlights": ["Hybrid SSR/CSR"],
                        "technologies": ["Litestar", "Angular"],
                        "url": "https://example.com",
                    },
                ],
            },
        ]
        content = self.factory.core.resume_content(
            full_name="Dmitriy",
            role="Backend engineer",
            summary="Summary",
            experience=experience,
        )
        self.use_case.create_resume.return_value = self.factory.core.resume(
            resume_id=2,
            title="Target resume",
            language=LanguageEnum.EN,
            content=content,
            created_at="2026-01-01T03:04:05",
            updated_at="2026-01-01T03:04:05",
        )

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(
                title="Target resume",
                language="en",
                content=self.factory.api.resume_content(
                    full_name="Dmitriy",
                    role="Backend engineer",
                    summary="Summary",
                    experience=api_experience,
                ),
            ),
        )

        assert response.status_code == codes.CREATED, response.content
        assert response.json()["id"] == 2
        assert response.json()["language"] == "en"
        assert response.json()["content"]["profile"]["phone"] == ""
        assert response.json()["content"]["experience"][0]["currentStatus"] == "current"
        assert response.json()["content"]["experience"][0]["projects"][0]["name"] == "Portfolio"
        assert response_has_no_resume_localized_field_names(value=response.json())
        assert_resume_response_nulls_are_dates_only(value=response.json()["content"])
        self.use_case.create_resume.assert_called_once_with(
            params=ResumeCreateParams(
                title="Target resume",
                language=LanguageEnum.EN,
                content=content,
                author_username="test",
            ),
        )

    def test_update_resume_maps_payload_to_params(self) -> None:
        content = self.factory.core.resume_content(summary="Updated")
        self.use_case.update_resume.return_value = self.factory.core.resume(
            resume_id=3,
            title="Updated resume",
            language=LanguageEnum.EN,
            content=content,
            updated_at="2026-01-03T03:04:05",
        )

        response = self.api.put_update_resume(
            resume_id=3,
            data=self.factory.api.resume_request(
                title="Updated resume",
                language="en",
                content=self.factory.api.resume_content(summary="Updated"),
            ),
        )

        assert response.status_code == codes.OK, response.content
        assert response.json()["title"] == "Updated resume"
        assert response.json()["language"] == "en"
        self.use_case.update_resume.assert_called_once_with(
            resume_id=IntId(3),
            params=ResumeUpdateParams(
                title="Updated resume",
                language=LanguageEnum.EN,
                content=content,
            ),
            author_username="test",
        )

    def test_create_resume_rejects_missing_language(self) -> None:
        data = self.factory.api.resume_request()
        data.pop("language")

        response = self.api.post_create_resume(data=data)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.create_resume.assert_not_called()

    def test_create_resume_rejects_unknown_language(self) -> None:
        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(language="de"),
        )

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.create_resume.assert_not_called()

    def test_get_resume(self) -> None:
        self.use_case.get_resume.return_value = self.factory.core.resume(
            resume_id=3,
            title="Backend resume",
            updated_at="2026-01-03T03:04:05",
        )

        response = self.api.get_admin_resume(resume_id=3)

        assert response.status_code == codes.OK, response.content
        assert response.json()["id"] == 3
        assert response.json()["language"] == "ru"
        assert response_has_no_resume_localized_field_names(value=response.json())
        assert_resume_response_nulls_are_dates_only(value=response.json()["content"])
        self.use_case.get_resume.assert_called_once_with(
            resume_id=IntId(3),
            author_username="test",
        )

    def test_get_resume_not_found(self) -> None:
        self.use_case.get_resume.side_effect = ResumeNotFoundError()

        response = self.api.get_admin_resume(resume_id=404)

        assert response.status_code == codes.NOT_FOUND
        assert response.json()["message"] == ResumeNotFoundError.message
        self.use_case.get_resume.assert_called_once_with(
            resume_id=IntId(404),
            author_username="test",
        )

    def test_delete_resume_not_found(self) -> None:
        self.use_case.delete_resume.side_effect = ResumeNotFoundError()

        response = self.api.delete_resume(resume_id=404)

        assert response.status_code == codes.NOT_FOUND
        assert response.json()["message"] == ResumeNotFoundError.message
        self.use_case.delete_resume.assert_called_once_with(
            resume_id=IntId(404),
            author_username="test",
        )

    def test_delete_resume(self) -> None:
        response = self.api.delete_resume(resume_id=3)

        assert response.status_code == codes.NO_CONTENT
        self.use_case.delete_resume.assert_called_once_with(
            resume_id=IntId(3),
            author_username="test",
        )

    def test_requires_authentication(self) -> None:
        response = self.no_auth_api.get_admin_resumes()

        assert response.status_code == codes.UNAUTHORIZED
        self.use_case.list_resumes.assert_not_called()

    def test_requires_admin_role(self) -> None:
        self.authentication_use_case.authenticate.return_value = JwtUser(
            username="moderator",
            role=RoleEnum.MODERATOR,
        )

        response = self.api.get_admin_resumes()

        assert response.status_code == codes.UNAUTHORIZED
        self.use_case.list_resumes.assert_not_called()


RESUME_RESPONSE_ALLOWED_NULL_KEYS = frozenset({"startDate", "endDate", "issuedOn", "expiresOn"})
RESUME_LOCALIZED_FIELD_SUFFIXES = ("Ru", "En")


def assert_resume_response_nulls_are_dates_only(*, value: object, key: str | None = None) -> None:
    if value is None:
        assert key in RESUME_RESPONSE_ALLOWED_NULL_KEYS
        return
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            assert_resume_response_nulls_are_dates_only(value=child_value, key=child_key)
        return
    if isinstance(value, list):
        for item in value:
            assert_resume_response_nulls_are_dates_only(value=item, key=key)


def response_has_no_resume_localized_field_names(*, value: object) -> bool:
    if isinstance(value, dict):
        for key, child_value in value.items():
            assert not key.endswith(RESUME_LOCALIZED_FIELD_SUFFIXES), key
            response_has_no_resume_localized_field_names(value=child_value)
    if isinstance(value, list):
        for item in value:
            response_has_no_resume_localized_field_names(value=item)
    return True
