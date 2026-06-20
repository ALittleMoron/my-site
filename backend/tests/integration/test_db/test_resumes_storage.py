from datetime import UTC, date, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import String, cast, select

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
        content = full_content(summary="Builds reliable backend systems.")

        created = await self.storage.create_resume(
            params=ResumeCreateParams(
                title="Backend engineer",
                language=LanguageEnum.EN,
                content=content,
                author_username="admin",
            ),
        )
        loaded = await self.storage.get_resume(resume_id=created.id, author_username="admin")
        created_row = await self.db_session.get(ResumeModel, created.id)

        assert loaded.id == created.id
        assert loaded.title == "Backend engineer"
        assert loaded.language == LanguageEnum.EN
        assert loaded.author_username == "admin"
        assert loaded.content == content
        assert loaded.created_at.tzinfo == UTC
        assert loaded.updated_at.tzinfo == UTC
        assert created_row is not None
        assert created_row.language is LanguageEnum.EN
        assert created_row.content["experience"][0]["current_status"] == "current"
        assert created_row.content["experience"][0]["company"] == "Company"
        assert "is_current" not in created_row.content["experience"][0]
        assert "company_ru" not in created_row.content["experience"][0]

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
                language=LanguageEnum.RU,
                content=full_content(summary="Старое описание."),
                author_username="admin",
            ),
        )
        replacement = empty_content(summary="Новое описание.")
        updated_at = created.updated_at + timedelta(minutes=5)

        updated = await self.storage.update_resume(
            resume=Resume(
                id=created.id,
                title="Platform engineer",
                language=LanguageEnum.RU,
                content=replacement,
                author_username="admin",
                created_at=created.created_at,
                updated_at=updated_at,
            ),
        )

        assert updated.title == "Platform engineer"
        assert updated.language == LanguageEnum.RU
        assert updated.content == replacement
        assert updated.created_at == created.created_at
        assert updated.updated_at == updated_at

    async def test_get_resume_normalizes_nullable_content_jsonb(self) -> None:
        model = ResumeModel(
            id=IntId(50),
            title="Nullable resume",
            language=LanguageEnum.RU,
            author_username="admin",
            content=nullable_content_json(),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            updated_at=datetime(2026, 1, 2, tzinfo=UTC),
        )
        self.db_session.add(model)
        await self.db_session.flush()

        loaded = await self.storage.get_resume(resume_id=IntId(50), author_username="admin")

        assert loaded.content.profile.full_name == ""
        assert loaded.content.profile.phone == ""
        assert loaded.content.summary.text == ""
        assert loaded.content.skills[0].category == ""
        assert loaded.content.skills[0].items == []
        assert loaded.content.experience[0].location == ""
        assert loaded.content.experience[0].current_status == ResumeCurrentStatusEnum.NOT_SET
        assert loaded.content.experience[0].end_date is None
        assert loaded.content.experience[0].highlights == []
        assert loaded.content.experience[0].projects[0].url == ""
        assert loaded.content.experience[0].projects[0].technologies == []

    async def test_delete_resume_removes_row(self) -> None:
        created = await self.storage.create_resume(
            params=ResumeCreateParams(
                title="Backend engineer",
                language=LanguageEnum.RU,
                content=full_content(summary="Удаляемое резюме."),
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
            language=LanguageEnum.RU,
            content=empty_content(summary=""),
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
            language=LanguageEnum.RU,
            content=empty_content(summary=""),
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
                language=LanguageEnum.RU,
                content=full_content(summary=title),
                author_username=author_username,
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
                updated_at=updated_at,
            ),
        )
        self.db_session.add(model)
        await self.db_session.flush()


def full_content(*, summary: str) -> ResumeContent:
    return ResumeContent(
        profile=ResumeProfile(
            full_name="Dmitriy Ivanov",
            role="Backend engineer",
            location="Moscow",
            email="dmitriy@example.com",
            phone="+79990000000",
            website_url="https://example.com",
            linkedin_url="https://linkedin.com/in/dmitriy",
            github_url="https://github.com/dmitriy",
            telegram="@dmitriy",
        ),
        summary=ResumeSummary(
            text=summary,
        ),
        skills=[
            ResumeSkillGroup(
                category="Languages",
                items=["Python", "TypeScript"],
            ),
        ],
        experience=[
            ResumeExperienceItem(
                company="Company",
                position="Engineer",
                location="Moscow",
                start_date=date(2023, 1, 1),
                end_date=None,
                current_status=ResumeCurrentStatusEnum.CURRENT,
                summary="Built platform services.",
                highlights=["Reduced response time"],
                technologies=["Python", "PostgreSQL"],
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
        ],
        education=[
            ResumeEducationItem(
                institution="University",
                degree="Bachelor",
                field="Computer science",
                location="Moscow",
                start_date=date(2014, 9, 1),
                end_date=date(2018, 6, 30),
                description="Applied computer science",
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
                issued_on=date(2025, 1, 1),
                expires_on=None,
                credential_url="https://example.com/cert",
            ),
        ],
        additional_sections=[
            ResumeAdditionalSection(
                title="Publications",
                items=[
                    ResumeAdditionalSectionItem(
                        title="Article",
                        description="Technical write-up",
                        url="https://example.com/article",
                    ),
                ],
            ),
        ],
    )


def nullable_content_json() -> dict[str, object]:
    return {
        "profile": {
            "full_name": None,
            "role": None,
            "location": None,
            "email": None,
            "phone": None,
            "website_url": None,
            "linkedin_url": None,
            "github_url": None,
            "telegram": None,
        },
        "summary": {
            "text": None,
        },
        "skills": [
            {
                "category": None,
                "items": None,
            },
        ],
        "experience": [
            {
                "company": None,
                "position": None,
                "location": None,
                "start_date": None,
                "end_date": None,
                "current_status": None,
                "summary": None,
                "highlights": None,
                "technologies": [],
                "projects": [
                    {
                        "name": None,
                        "role": None,
                        "description": None,
                        "highlights": [],
                        "technologies": None,
                        "url": None,
                    },
                ],
            },
        ],
        "education": [],
        "languages": [],
        "certifications": [],
        "additional_sections": [],
    }


def empty_content(*, summary: str) -> ResumeContent:
    return ResumeContent(
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
        summary=ResumeSummary(text=summary),
        skills=[],
        experience=[],
        education=[],
        languages=[],
        certifications=[],
        additional_sections=[],
    )
