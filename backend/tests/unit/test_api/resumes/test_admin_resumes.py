from dataclasses import replace

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
from core.types import IntId
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
        assert listed_resume["id"] == 1
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

        self.asserts.status(response=response, expected_status=codes.CREATED)
        body = response.json()
        assert body["id"] == 2
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
        assert body["id"] == 3
        assert body["language"] == "ru"
        self.asserts.resume_response_contract(value=body)
        self.use_case.get_resume.assert_called_once_with(
            resume_id=IntId(3),
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
            resume_id=IntId(404),
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
        assert response.headers["content-disposition"] == 'attachment; filename="resume-3.pdf"'
        self.use_case.export_resume.assert_called_once_with(
            resume_id=IntId(3),
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
        assert response.headers["content-disposition"] == 'attachment; filename="resume-5.docx"'
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
            resume_id=IntId(404),
            author_username="test",
        )

    def test_delete_resume(self) -> None:
        response = self.api.delete_resume(resume_id=3)

        self.asserts.status(response=response, expected_status=codes.NO_CONTENT)
        self.use_case.delete_resume.assert_called_once_with(
            resume_id=IntId(3),
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
