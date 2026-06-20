from datetime import UTC, date, datetime
from typing import Any
from unittest.mock import Mock

import pytest

from core.i18n.enums import LanguageEnum
from core.resumes.enums import ResumeCurrentStatusEnum
from core.resumes.exceptions import ResumeNotFoundError
from core.resumes.schemas import (
    Resume,
    ResumeAdditionalSection,
    ResumeAdditionalSectionItem,
    ResumeCertificationItem,
    ResumeContent,
    ResumeCreateParams,
    ResumeEducationItem,
    ResumeExperienceItem,
    ResumeFilters,
    ResumeLanguageItem,
    ResumeProfile,
    ResumeProjectItem,
    Resumes,
    ResumeSkillGroup,
    ResumeSummary,
    ResumeUpdateParams,
)
from core.resumes.storages import ResumesStorage
from core.resumes.use_cases import ResumesUseCase
from core.types import IntId


def build_content(*, summary: str, skill_items: list[str]) -> ResumeContent:
    return ResumeContent(
        profile=ResumeProfile(
            full_name="Dmitriy Ivanov",
            role="Backend engineer",
            location="Moscow",
            email="dmitriy@example.com",
            phone="",
            website_url="https://example.com",
            linkedin_url="",
            github_url="https://github.com/dmitriy",
            telegram="@dmitriy",
        ),
        summary=ResumeSummary(
            text=summary,
        ),
        skills=[
            ResumeSkillGroup(
                category="Languages",
                items=skill_items,
            ),
        ],
        experience=[
            ResumeExperienceItem(
                company="Company",
                position="Engineer",
                location="",
                start_date=date(2023, 1, 1),
                end_date=None,
                current_status=ResumeCurrentStatusEnum.CURRENT,
                summary="",
                highlights=["Launched service"],
                technologies=["Python", "PostgreSQL"],
                projects=[
                    ResumeProjectItem(
                        name="Portfolio",
                        role="",
                        description="Site and knowledge base",
                        highlights=[],
                        technologies=["Litestar", "Angular"],
                        url="https://example.com",
                    ),
                ],
            ),
        ],
        education=[
            ResumeEducationItem(
                institution="University",
                degree="",
                field="Computer science",
                location="",
                start_date=None,
                end_date=None,
                description="",
            ),
        ],
        languages=[
            ResumeLanguageItem(
                name="English",
                proficiency="C1",
            ),
        ],
        certifications=[
            ResumeCertificationItem(
                name="Certificate",
                issuer="Provider",
                issued_on=None,
                expires_on=None,
                credential_url="",
            ),
        ],
        additional_sections=[
            ResumeAdditionalSection(
                title="Publications",
                items=[
                    ResumeAdditionalSectionItem(
                        title="Article",
                        description="",
                        url="",
                    ),
                ],
            ),
        ],
    )


def build_resume(
    *,
    resume_id: IntId,
    content: ResumeContent,
    author_username: str = "test",
    language: LanguageEnum = LanguageEnum.EN,
) -> Resume:
    return Resume(
        id=resume_id,
        title="Backend engineer",
        language=language,
        content=content,
        author_username=author_username,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 2, tzinfo=UTC),
    )


class TestResumesUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=ResumesStorage)
        self.use_case = ResumesUseCase(storage=self.storage)

    def test_resume_filters_require_explicit_values(self) -> None:
        missing_filter_values: dict[str, Any] = {}

        with pytest.raises(TypeError, match="required keyword-only arguments"):
            ResumeFilters(**missing_filter_values)

    async def test_list_resumes_builds_page_from_storage_rows(self) -> None:
        filters = ResumeFilters(
            page=2,
            page_size=10,
            search_query="backend",
            author_username="test",
        )
        resume = build_resume(
            resume_id=IntId(1),
            content=build_content(summary="Builds reliable systems.", skill_items=["Python"]),
        )
        self.storage.list_resumes.return_value = ([resume], 21)

        result = await self.use_case.list_resumes(filters=filters)

        assert result == Resumes(values=[resume], total_count=21, total_pages=3)
        assert filters.limit == 10
        assert filters.offset == 10
        self.storage.list_resumes.assert_called_once_with(filters=filters)

    async def test_list_resumes_requires_pagination_before_storage_call(self) -> None:
        with pytest.raises(ValueError, match="pagination required"):
            await self.use_case.list_resumes(
                filters=ResumeFilters(
                    page=None,
                    page_size=None,
                    search_query=None,
                    author_username="test",
                ),
            )

        self.storage.list_resumes.assert_not_called()

    async def test_get_resume_delegates_to_storage(self) -> None:
        expected = build_resume(
            resume_id=IntId(1),
            content=build_content(summary="Builds reliable systems.", skill_items=["Python"]),
        )
        self.storage.get_resume.return_value = expected

        result = await self.use_case.get_resume(resume_id=IntId(1), author_username="test")

        assert result == expected
        self.storage.get_resume.assert_called_once_with(
            resume_id=IntId(1),
            author_username="test",
        )

    async def test_get_resume_propagates_not_found(self) -> None:
        self.storage.get_resume.side_effect = ResumeNotFoundError

        with pytest.raises(ResumeNotFoundError):
            await self.use_case.get_resume(resume_id=IntId(404), author_username="test")

    async def test_create_resume_persists_explicit_content(self) -> None:
        content = build_content(summary="Builds reliable systems.", skill_items=["Python"])
        params = ResumeCreateParams(
            title="Backend engineer",
            language=LanguageEnum.EN,
            content=content,
            author_username="test",
        )
        expected = build_resume(resume_id=IntId(1), content=content)
        self.storage.create_resume.return_value = expected

        result = await self.use_case.create_resume(params=params)

        assert result == expected
        self.storage.create_resume.assert_called_once_with(params=params)

    async def test_update_resume_replaces_whole_content(self) -> None:
        existing_content = build_content(
            summary="Old summary.",
            skill_items=["Python", "SQL"],
        )
        existing_resume = build_resume(
            resume_id=IntId(1),
            content=existing_content,
            author_username="original-author",
        )
        replacement_content = ResumeContent(
            profile=ResumeProfile(
                full_name="",
                role="",
                location="",
                email="",
                phone="",
                website_url="",
                linkedin_url="",
                github_url="",
                telegram="",
            ),
            summary=ResumeSummary(
                text="Updated summary.",
            ),
            skills=[],
            experience=[],
            education=[],
            languages=[],
            certifications=[],
            additional_sections=[],
        )
        params = ResumeUpdateParams(
            title="Platform engineer",
            language=LanguageEnum.RU,
            content=replacement_content,
        )
        expected = build_resume(
            resume_id=IntId(1),
            content=replacement_content,
            author_username="original-author",
        )
        self.storage.get_resume.return_value = existing_resume
        self.storage.update_resume.return_value = expected

        result = await self.use_case.update_resume(
            resume_id=IntId(1),
            params=params,
            author_username="original-author",
        )

        assert result == expected
        self.storage.get_resume.assert_called_once_with(
            resume_id=IntId(1),
            author_username="original-author",
        )
        self.storage.update_resume.assert_called_once()
        updated_resume = self.storage.update_resume.call_args.kwargs["resume"]
        assert updated_resume.id == existing_resume.id
        assert updated_resume.author_username == "original-author"
        assert updated_resume.created_at == existing_resume.created_at
        assert updated_resume.updated_at > existing_resume.updated_at
        assert updated_resume.title == "Platform engineer"
        assert updated_resume.language == LanguageEnum.RU
        assert updated_resume.content == replacement_content
        assert updated_resume.content.experience == []

    async def test_delete_resume_delegates_to_storage(self) -> None:
        await self.use_case.delete_resume(resume_id=IntId(1), author_username="test")

        self.storage.delete_resume.assert_called_once_with(
            resume_id=IntId(1),
            author_username="test",
        )
