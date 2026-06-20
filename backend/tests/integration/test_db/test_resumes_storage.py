from datetime import UTC, date, datetime, timedelta

import pytest
import pytest_asyncio

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
    ResumeSkillGroup,
    ResumeSummary,
)
from core.types import IntId
from infra.postgresql.models import ResumeModel
from infra.postgresql.storages.resumes import ResumesDatabaseStorage
from tests.fixtures import StorageFixture


class TestResumesDatabaseStorage(StorageFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.storage = ResumesDatabaseStorage(session=self.db_session)

    async def test_create_and_get_resume_roundtrips_full_content_jsonb(self) -> None:
        content = full_content(summary_ru="Создаёт надежные backend-системы.")

        created = await self.storage.create_resume(
            params=ResumeCreateParams(
                title="Backend engineer",
                content=content,
                author_username="admin",
            ),
        )
        loaded = await self.storage.get_resume(resume_id=created.id, author_username="admin")

        assert loaded.id == created.id
        assert loaded.title == "Backend engineer"
        assert loaded.author_username == "admin"
        assert loaded.content == content
        assert loaded.created_at.tzinfo == UTC
        assert loaded.updated_at.tzinfo == UTC

    async def test_list_resumes_orders_by_updated_at_then_id_and_paginates(self) -> None:
        await self.create_resume_row(
            resume_id=IntId(1),
            title="Older",
            author_username="admin",
            updated_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        await self.create_resume_row(
            resume_id=IntId(2),
            title="Tie lower id",
            author_username="admin",
            updated_at=datetime(2026, 1, 3, tzinfo=UTC),
        )
        await self.create_resume_row(
            resume_id=IntId(3),
            title="Tie higher id",
            author_username="admin",
            updated_at=datetime(2026, 1, 3, tzinfo=UTC),
        )
        await self.create_resume_row(
            resume_id=IntId(4),
            title="Other author",
            author_username="other-admin",
            updated_at=datetime(2026, 1, 3, tzinfo=UTC),
        )

        resumes, total_count = await self.storage.list_resumes(
            filters=ResumeFilters(
                page=1,
                page_size=2,
                search_query=None,
                author_username="admin",
            ),
        )

        assert [resume.id for resume in resumes] == [IntId(3), IntId(2)]
        assert total_count == 3

    async def test_update_resume_replaces_content(self) -> None:
        created = await self.storage.create_resume(
            params=ResumeCreateParams(
                title="Backend engineer",
                content=full_content(summary_ru="Старое описание."),
                author_username="admin",
            ),
        )
        replacement = empty_content(summary_ru="Новое описание.", summary_en="Updated summary.")
        updated_at = created.updated_at + timedelta(minutes=5)

        updated = await self.storage.update_resume(
            resume=Resume(
                id=created.id,
                title="Platform engineer",
                content=replacement,
                author_username="admin",
                created_at=created.created_at,
                updated_at=updated_at,
            ),
        )

        assert updated.title == "Platform engineer"
        assert updated.content == replacement
        assert updated.created_at == created.created_at
        assert updated.updated_at == updated_at

    async def test_delete_resume_removes_row(self) -> None:
        created = await self.storage.create_resume(
            params=ResumeCreateParams(
                title="Backend engineer",
                content=full_content(summary_ru="Удаляемое резюме."),
                author_username="admin",
            ),
        )

        await self.storage.delete_resume(resume_id=created.id, author_username="admin")

        with pytest.raises(ResumeNotFoundError):
            await self.storage.get_resume(resume_id=created.id, author_username="admin")

    async def test_other_author_resume_operations_raise_domain_error(self) -> None:
        await self.create_resume_row(
            resume_id=IntId(10),
            title="Other author",
            author_username="other-admin",
            updated_at=datetime(2026, 1, 3, tzinfo=UTC),
        )
        other_author_resume = Resume(
            id=IntId(10),
            title="Attempted update",
            content=empty_content(summary_ru=None, summary_en=None),
            author_username="admin",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            updated_at=datetime(2026, 1, 2, tzinfo=UTC),
        )

        with pytest.raises(ResumeNotFoundError):
            await self.storage.get_resume(resume_id=IntId(10), author_username="admin")
        with pytest.raises(ResumeNotFoundError):
            await self.storage.update_resume(resume=other_author_resume)
        with pytest.raises(ResumeNotFoundError):
            await self.storage.delete_resume(resume_id=IntId(10), author_username="admin")

    async def test_missing_resume_operations_raise_domain_error(self) -> None:
        missing_resume = Resume(
            id=IntId(404),
            title="Missing",
            content=empty_content(summary_ru=None, summary_en=None),
            author_username="admin",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            updated_at=datetime(2026, 1, 2, tzinfo=UTC),
        )

        with pytest.raises(ResumeNotFoundError):
            await self.storage.get_resume(resume_id=IntId(404), author_username="admin")
        with pytest.raises(ResumeNotFoundError):
            await self.storage.update_resume(resume=missing_resume)
        with pytest.raises(ResumeNotFoundError):
            await self.storage.delete_resume(resume_id=IntId(404), author_username="admin")

    async def create_resume_row(
        self,
        *,
        resume_id: IntId,
        title: str,
        author_username: str,
        updated_at: datetime,
    ) -> None:
        model = ResumeModel.from_domain_schema(
            resume=Resume(
                id=resume_id,
                title=title,
                content=full_content(summary_ru=title),
                author_username=author_username,
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
                updated_at=updated_at,
            ),
        )
        self.db_session.add(model)
        await self.db_session.flush()


def full_content(*, summary_ru: str) -> ResumeContent:
    return ResumeContent(
        profile=ResumeProfile(
            full_name="Dmitriy Ivanov",
            role_ru="Бэкенд-инженер",
            role_en="Backend engineer",
            location_ru="Москва",
            location_en="Moscow",
            email="dmitriy@example.com",
            phone="+79990000000",
            website_url="https://example.com",
            linkedin_url="https://linkedin.com/in/dmitriy",
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
                items=["Python", "TypeScript"],
            ),
        ],
        experience=[
            ResumeExperienceItem(
                company_ru="Компания",
                company_en="Company",
                position_ru="Инженер",
                position_en="Engineer",
                location_ru="Москва",
                location_en="Moscow",
                start_date=date(2023, 1, 1),
                end_date=None,
                is_current=True,
                summary_ru="Разрабатывал платформенные сервисы.",
                summary_en="Built platform services.",
                highlights_ru=["Сократил время отклика"],
                highlights_en=["Reduced response time"],
                technologies=["Python", "PostgreSQL"],
                projects=[
                    ResumeProjectItem(
                        name_ru="Портфолио",
                        name_en="Portfolio",
                        role_ru="Автор",
                        role_en="Creator",
                        description_ru="Сайт и база знаний",
                        description_en="Site and knowledge base",
                        highlights_ru=["Гибридный SSR/CSR"],
                        highlights_en=["Hybrid SSR/CSR"],
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
                degree_ru="Бакалавр",
                degree_en="Bachelor",
                field_ru="Информатика",
                field_en="Computer science",
                location_ru="Москва",
                location_en="Moscow",
                start_date=date(2014, 9, 1),
                end_date=date(2018, 6, 30),
                description_ru="Прикладная информатика",
                description_en="Applied computer science",
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
                issued_on=date(2025, 1, 1),
                expires_on=None,
                credential_url="https://example.com/cert",
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
                        description_ru="Технический разбор",
                        description_en="Technical write-up",
                        url="https://example.com/article",
                    ),
                ],
            ),
        ],
    )


def empty_content(*, summary_ru: str | None, summary_en: str | None) -> ResumeContent:
    return ResumeContent(
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
        summary=ResumeSummary(text_ru=summary_ru, text_en=summary_en),
        skills=[],
        experience=[],
        education=[],
        languages=[],
        certifications=[],
        additional_sections=[],
    )
