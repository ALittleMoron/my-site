from datetime import UTC, date, datetime
from typing import Any
from unittest.mock import Mock

import pytest

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


def build_content(*, summary_ru: str, skill_items: list[str]) -> ResumeContent:
    return ResumeContent(
        profile=ResumeProfile(
            full_name="Dmitriy Ivanov",
            role_ru="Бэкенд-инженер",
            role_en="Backend engineer",
            location_ru="Москва",
            location_en="Moscow",
            email="dmitriy@example.com",
            phone=None,
            website_url="https://example.com",
            linkedin_url=None,
            github_url="https://github.com/dmitriy",
            telegram="@dmitriy",
        ),
        summary=ResumeSummary(
            text_ru=summary_ru,
            text_en="Builds reliable backend systems.",
        ),
        skills=[
            ResumeSkillGroup(
                category_ru="Языки",
                category_en="Languages",
                items=skill_items,
            ),
        ],
        experience=[
            ResumeExperienceItem(
                company_ru="Компания",
                company_en="Company",
                position_ru="Инженер",
                position_en="Engineer",
                location_ru=None,
                location_en=None,
                start_date=date(2023, 1, 1),
                end_date=None,
                is_current=True,
                summary_ru=None,
                summary_en=None,
                highlights_ru=["Запустил сервис"],
                highlights_en=["Launched service"],
                technologies=["Python", "PostgreSQL"],
                projects=[
                    ResumeProjectItem(
                        name_ru="Портфолио",
                        name_en="Portfolio",
                        role_ru=None,
                        role_en=None,
                        description_ru="Сайт и база знаний",
                        description_en="Site and knowledge base",
                        highlights_ru=[],
                        highlights_en=[],
                        technologies=["Litestar", "Angular"],
                        url="https://example.com",
                    ),
                ],
            ),
        ],
        education=[
            ResumeEducationItem(
                institution_ru="Университет",
                institution_en="University",
                degree_ru=None,
                degree_en=None,
                field_ru="Информатика",
                field_en="Computer science",
                location_ru=None,
                location_en=None,
                start_date=None,
                end_date=None,
                description_ru=None,
                description_en=None,
            ),
        ],
        languages=[
            ResumeLanguageItem(
                name_ru="Английский",
                name_en="English",
                proficiency_ru="C1",
                proficiency_en="C1",
            ),
        ],
        certifications=[
            ResumeCertificationItem(
                name_ru="Сертификат",
                name_en="Certificate",
                issuer_ru="Провайдер",
                issuer_en="Provider",
                issued_on=None,
                expires_on=None,
                credential_url=None,
            ),
        ],
        additional_sections=[
            ResumeAdditionalSection(
                title_ru="Публикации",
                title_en="Publications",
                items=[
                    ResumeAdditionalSectionItem(
                        title_ru="Статья",
                        title_en="Article",
                        description_ru=None,
                        description_en=None,
                        url=None,
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
) -> Resume:
    return Resume(
        id=resume_id,
        title="Backend engineer",
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
            content=build_content(summary_ru="Создает надежные системы.", skill_items=["Python"]),
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
            content=build_content(summary_ru="Создает надежные системы.", skill_items=["Python"]),
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
        content = build_content(summary_ru="Создает надежные системы.", skill_items=["Python"])
        params = ResumeCreateParams(
            title="Backend engineer",
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
            summary_ru="Старое описание.",
            skill_items=["Python", "SQL"],
        )
        existing_resume = build_resume(
            resume_id=IntId(1),
            content=existing_content,
            author_username="original-author",
        )
        replacement_content = ResumeContent(
            profile=ResumeProfile(
                full_name=None,
                role_ru=None,
                role_en=None,
                location_ru=None,
                location_en=None,
                email=None,
                phone=None,
                website_url=None,
                linkedin_url=None,
                github_url=None,
                telegram=None,
            ),
            summary=ResumeSummary(
                text_ru="Новое описание.",
                text_en="Updated summary.",
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
        assert updated_resume.content == replacement_content
        assert updated_resume.content.experience == []

    async def test_delete_resume_delegates_to_storage(self) -> None:
        await self.use_case.delete_resume(resume_id=IntId(1), author_username="test")

        self.storage.delete_resume.assert_called_once_with(
            resume_id=IntId(1),
            author_username="test",
        )
