from dataclasses import replace
from datetime import date
from typing import cast

import pytest
import pytest_asyncio
from httpx import codes

from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser
from core.i18n.enums import LanguageEnum
from core.resumes.enums import ResumeCurrentStatusEnum, ResumeExportFormatEnum
from core.resumes.exceptions import ResumeNotFoundError
from core.resumes.schemas import (
    ResumeCreateParams,
    ResumeExperienceItem,
    ResumeExport,
    ResumeExportParams,
    ResumeFilters,
    ResumeProjectItem,
    ResumeUpdateParams,
)
from tests.test_cases import ApiTestCase


class TestAdminResumesAPI(ApiTestCase):
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

        self.asserts.status(response=response, expected_status=codes.OK)
        body = response.json()
        listed_resume = body["resumes"][0]
        assert body["totalCount"] == 1
        assert body["totalPages"] == 1
        assert listed_resume["id"] == self.factory.core.hex_id(1)
        assert listed_resume["title"] == "Backend resume"
        assert listed_resume["language"] == "ru"
        assert listed_resume["content"]["profile"]["fullName"] == "Candidate Name"
        assert listed_resume["content"]["profile"]["phone"] == ""
        self.asserts.resume_response_contract(value=listed_resume)
        self.use_case.list_resumes.assert_called_once_with(
            filters=ResumeFilters(
                page=2,
                page_size=10,
                search_query=None,
                author_username="test",
            ),
        )

    def test_list_resumes_allows_legacy_bare_profile_urls(self) -> None:
        content = self.factory.core.resume_content()
        content = replace(
            content,
            profile=replace(
                content.profile,
                linkedin_url="www.linkedin.com/in/dmitriy-lunev",
                github_url="github.com/ALittleMoron",
            ),
        )
        resume = self.factory.core.resume(
            resume_id=1,
            title="Backend resume",
            content=content,
        )
        self.use_case.list_resumes.return_value = self.factory.core.resumes(
            values=[resume],
            total_count=1,
            total_pages=1,
        )

        response = self.api.get_admin_resumes(page=1, page_size=10)

        self.asserts.status(response=response, expected_status=codes.OK)
        profile = response.json()["resumes"][0]["content"]["profile"]
        assert profile["linkedinUrl"] == "www.linkedin.com/in/dmitriy-lunev"
        assert profile["githubUrl"] == "github.com/ALittleMoron"

    def test_create_resume_maps_payload_to_params(self) -> None:
        experience = [
            ResumeExperienceItem(
                company="Company",
                position="Engineer",
                location="",
                start_date=date(2024, 1, 1),
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
                "startDate": "2024-01-01",
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

        self.asserts.status(response=response, expected_status=codes.CREATED)
        body = response.json()
        assert body["id"] == self.factory.core.hex_id(2)
        assert body["language"] == "en"
        assert body["content"]["profile"]["phone"] == ""
        assert body["content"]["experience"][0]["currentStatus"] == "current"
        assert body["content"]["experience"][0]["projects"][0]["name"] == "Portfolio"
        self.asserts.resume_response_contract(value=body)
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

        self.asserts.status(response=response, expected_status=codes.OK)
        body = response.json()
        assert body["title"] == "Updated resume"
        assert body["language"] == "en"
        self.use_case.update_resume.assert_called_once_with(
            resume_id=self.factory.core.hex_id(3),
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

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    def test_create_resume_rejects_unknown_language(self) -> None:
        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(language="de"),
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    def test_create_resume_rejects_whitespace_title(self) -> None:
        response = self.api.post_create_resume(data=self.factory.api.resume_request(title="   "))

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    def test_create_resume_allows_empty_repeatable_sections(self) -> None:
        content = self.factory.api.resume_content()
        content["skills"] = []
        content["experience"] = []
        content["education"] = []
        content["languages"] = []
        content["certifications"] = []
        content["additionalSections"] = []
        domain_content = self.factory.core.resume_content(skills=[], experience=[])
        self.use_case.create_resume.return_value = self.factory.core.resume(
            resume_id=2,
            content=domain_content,
        )

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content),
        )

        self.asserts.status(response=response, expected_status=codes.CREATED)
        self.use_case.create_resume.assert_called_once_with(
            params=ResumeCreateParams(
                title="Backend resume",
                language=LanguageEnum.RU,
                content=domain_content,
                author_username="test",
            ),
        )

    def test_create_resume_rejects_invalid_email(self) -> None:
        content = self.factory.api.resume_content()
        content["profile"]["email"] = "not-an-email"

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content)
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    def test_create_resume_rejects_invalid_url(self) -> None:
        content = self.factory.api.resume_content()
        content["profile"]["websiteUrl"] = "mailto:me@example.com"

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content)
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    @pytest.mark.parametrize("field", ["fullName", "role"])
    def test_create_resume_rejects_blank_required_profile_fields(self, field: str) -> None:
        content = self.factory.api.resume_content()
        content["profile"][field] = "   "
        self.use_case.create_resume.return_value = self.factory.core.resume()

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content)
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("category", "   "),
            ("items", ["Python", "   "]),
        ],
    )
    def test_create_resume_rejects_blank_required_skill_fields(
        self,
        field: str,
        value: object,
    ) -> None:
        content = self.factory.api.resume_content()
        content["skills"][0][field] = value
        self.use_case.create_resume.return_value = self.factory.core.resume()

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content)
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("company", "   "),
            ("position", "   "),
            ("startDate", None),
            ("highlights", ["Reduced latency", "   "]),
            ("technologies", ["Python", "   "]),
        ],
    )
    def test_create_resume_rejects_invalid_required_experience_fields(
        self,
        field: str,
        value: object,
    ) -> None:
        experience = valid_resume_experience_payload()
        experience[field] = value
        content = self.factory.api.resume_content(experience=[experience])
        self.use_case.create_resume.return_value = self.factory.core.resume()

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content)
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("name", "   "),
            ("role", "   "),
            ("highlights", ["Hybrid SSR/CSR", "   "]),
            ("technologies", ["Litestar", "   "]),
        ],
    )
    def test_create_resume_rejects_invalid_required_project_fields(
        self,
        field: str,
        value: object,
    ) -> None:
        experience = valid_resume_experience_payload()
        projects = cast("list[dict[str, object]]", experience["projects"])
        projects[0][field] = value
        content = self.factory.api.resume_content(experience=[experience])
        self.use_case.create_resume.return_value = self.factory.core.resume()

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content)
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("institution", "   "),
            ("degree", "   "),
            ("field", "   "),
            ("location", "   "),
            ("startDate", None),
            ("endDate", None),
        ],
    )
    def test_create_resume_rejects_invalid_required_education_fields(
        self,
        field: str,
        value: object,
    ) -> None:
        content = self.factory.api.resume_content()
        content["education"] = [valid_resume_education_payload()]
        content["education"][0][field] = value
        self.use_case.create_resume.return_value = self.factory.core.resume()

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content)
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    @pytest.mark.parametrize("field", ["name", "proficiency"])
    def test_create_resume_rejects_blank_required_language_fields(self, field: str) -> None:
        content = self.factory.api.resume_content()
        content["languages"] = [{"name": "English", "proficiency": "C1"}]
        content["languages"][0][field] = "   "
        self.use_case.create_resume.return_value = self.factory.core.resume()

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content)
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    def test_create_resume_rejects_blank_required_certification_name(self) -> None:
        content = self.factory.api.resume_content()
        content["certifications"] = [
            {
                "name": "   ",
                "issuer": "",
                "issuedOn": None,
                "expiresOn": None,
                "credentialUrl": "",
            },
        ]
        self.use_case.create_resume.return_value = self.factory.core.resume()

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content)
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            "blank_section_title",
            "empty_items",
            "blank_item_title",
        ],
    )
    def test_create_resume_rejects_invalid_required_additional_section_fields(
        self,
        case: str,
    ) -> None:
        content = self.factory.api.resume_content()
        content["additionalSections"] = [invalid_resume_additional_section_payload(case=case)]
        self.use_case.create_resume.return_value = self.factory.core.resume()

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content)
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    def test_export_resume_rejects_blank_required_profile_field(self) -> None:
        content = self.factory.api.resume_content()
        content["profile"]["fullName"] = "   "
        self.use_case.export_resume.return_value = ResumeExport(
            format=ResumeExportFormatEnum.PDF,
            content=b"%PDF-1.4",
        )

        response = self.api.post_export_resume(
            resume_id=3,
            data={
                "format": "pdf",
                **self.factory.api.resume_request(content=content),
            },
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.export_resume.assert_not_called()

    def test_create_resume_rejects_too_long_summary(self) -> None:
        content = self.factory.api.resume_content(summary="x" * 10_001)

        response = self.api.post_create_resume(
            data=self.factory.api.resume_request(content=content)
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.create_resume.assert_not_called()

    def test_get_resume(self) -> None:
        self.use_case.get_resume.return_value = self.factory.core.resume(
            resume_id=3,
            title="Backend resume",
            updated_at="2026-01-03T03:04:05",
        )

        response = self.api.get_admin_resume(resume_id=3)

        self.asserts.status(response=response, expected_status=codes.OK)
        body = response.json()
        assert body["id"] == self.factory.core.hex_id(3)
        assert body["language"] == "ru"
        self.asserts.resume_response_contract(value=body)
        self.use_case.get_resume.assert_called_once_with(
            resume_id=self.factory.core.hex_id(3),
            author_username="test",
        )

    def test_get_resume_not_found(self) -> None:
        self.use_case.get_resume.side_effect = ResumeNotFoundError()

        response = self.api.get_admin_resume(resume_id=404)

        self.asserts.error_message(
            response=response,
            expected_status=codes.NOT_FOUND,
            expected_message=ResumeNotFoundError.message,
        )
        self.use_case.get_resume.assert_called_once_with(
            resume_id=self.factory.core.hex_id(404),
            author_username="test",
        )

    def test_export_resume_pdf_from_current_payload(self) -> None:
        content = self.factory.core.resume_content(
            full_name="Dmitriy",
            role="Backend engineer",
            summary="Unsaved current summary",
        )
        self.use_case.export_resume.return_value = ResumeExport(
            format=ResumeExportFormatEnum.PDF,
            content=b"%PDF-1.4",
        )

        response = self.api.post_export_resume(
            resume_id=3,
            data={
                "format": "pdf",
                **self.factory.api.resume_request(
                    title="Target resume",
                    language="en",
                    content=self.factory.api.resume_content(
                        full_name="Dmitriy",
                        role="Backend engineer",
                        summary="Unsaved current summary",
                    ),
                ),
            },
        )

        self.asserts.status(response=response, expected_status=codes.OK)
        assert response.content == b"%PDF-1.4"
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == (
            f'attachment; filename="resume-{self.factory.core.hex_id(3)}.pdf"'
        )
        self.use_case.export_resume.assert_called_once_with(
            resume_id=self.factory.core.hex_id(3),
            params=ResumeExportParams(
                format=ResumeExportFormatEnum.PDF,
                title="Target resume",
                language=LanguageEnum.EN,
                content=content,
            ),
            author_username="test",
        )

    def test_export_resume_docx_from_current_payload(self) -> None:
        self.use_case.export_resume.return_value = ResumeExport(
            format=ResumeExportFormatEnum.DOCX,
            content=b"docx-bytes",
        )

        response = self.api.post_export_resume(
            resume_id=5,
            data={
                "format": "docx",
                **self.factory.api.resume_request(
                    title="Docx resume",
                    language="ru",
                ),
            },
        )

        self.asserts.status(response=response, expected_status=codes.OK)
        assert response.content == b"docx-bytes"
        assert (
            response.headers["content-type"]
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert response.headers["content-disposition"] == (
            f'attachment; filename="resume-{self.factory.core.hex_id(5)}.docx"'
        )
        self.use_case.export_resume.assert_called_once()

    def test_export_resume_rejects_unknown_format(self) -> None:
        response = self.api.post_export_resume(
            resume_id=3,
            data={
                "format": "xlsx",
                **self.factory.api.resume_request(),
            },
        )

        self.asserts.status(response=response, expected_status=codes.BAD_REQUEST)
        self.use_case.export_resume.assert_not_called()

    def test_export_resume_not_found(self) -> None:
        self.use_case.export_resume.side_effect = ResumeNotFoundError()

        response = self.api.post_export_resume(
            resume_id=404,
            data={
                "format": "pdf",
                **self.factory.api.resume_request(),
            },
        )

        self.asserts.error_message(
            response=response,
            expected_status=codes.NOT_FOUND,
            expected_message=ResumeNotFoundError.message,
        )
        self.use_case.export_resume.assert_called_once()

    def test_delete_resume_not_found(self) -> None:
        self.use_case.delete_resume.side_effect = ResumeNotFoundError()

        response = self.api.delete_resume(resume_id=404)

        self.asserts.error_message(
            response=response,
            expected_status=codes.NOT_FOUND,
            expected_message=ResumeNotFoundError.message,
        )
        self.use_case.delete_resume.assert_called_once_with(
            resume_id=self.factory.core.hex_id(404),
            author_username="test",
        )

    def test_delete_resume(self) -> None:
        response = self.api.delete_resume(resume_id=3)

        self.asserts.status(response=response, expected_status=codes.NO_CONTENT)
        self.use_case.delete_resume.assert_called_once_with(
            resume_id=self.factory.core.hex_id(3),
            author_username="test",
        )

    def test_requires_authentication(self) -> None:
        response = self.no_auth_api.get_admin_resumes()

        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)
        self.use_case.list_resumes.assert_not_called()

        response = self.no_auth_api.post_export_resume(
            resume_id=3,
            data={
                "format": "pdf",
                **self.factory.api.resume_request(),
            },
        )

        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)
        self.use_case.export_resume.assert_not_called()

    def test_requires_admin_role(self) -> None:
        self.authentication_use_case.authenticate.return_value = JwtUser(
            username="moderator",
            role=RoleEnum.MODERATOR,
        )

        response = self.api.get_admin_resumes()

        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)
        self.use_case.list_resumes.assert_not_called()

        response = self.api.post_export_resume(
            resume_id=3,
            data={
                "format": "pdf",
                **self.factory.api.resume_request(),
            },
        )

        self.asserts.status(response=response, expected_status=codes.UNAUTHORIZED)
        self.use_case.export_resume.assert_not_called()


def valid_resume_experience_payload() -> dict[str, object]:
    return {
        "company": "Company",
        "position": "Engineer",
        "location": "",
        "startDate": "2024-01-01",
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
                "technologies": ["Litestar"],
                "url": "https://example.com",
            },
        ],
    }


def valid_resume_education_payload() -> dict[str, object]:
    return {
        "institution": "University",
        "degree": "Bachelor",
        "field": "Computer science",
        "location": "Moscow",
        "startDate": "2014-09-01",
        "endDate": "2018-06-30",
        "description": "",
    }


def valid_resume_additional_item_payload(*, title: str = "Article") -> dict[str, object]:
    return {
        "title": title,
        "description": "",
        "url": "",
    }


def invalid_resume_additional_section_payload(*, case: str) -> dict[str, object]:
    if case == "blank_section_title":
        return {
            "title": "   ",
            "items": [valid_resume_additional_item_payload()],
        }
    if case == "empty_items":
        return {
            "title": "Publications",
            "items": [],
        }
    if case == "blank_item_title":
        return {
            "title": "Publications",
            "items": [valid_resume_additional_item_payload(title="   ")],
        }
    message = f"Unsupported additional section validation case: {case}"
    raise ValueError(message)
