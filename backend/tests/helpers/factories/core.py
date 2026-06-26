import re
import uuid
from datetime import UTC, date, datetime
from typing import Any

from core.articles.schemas import (
    Article,
    ArticleMetadata,
    ArticleReactionCounts,
    Articles,
    Tag,
    Tags,
)
from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser, User
from core.auth.types import Token
from core.competency_matrix.enums import GradeEnum, InterviewFrequencyEnum
from core.competency_matrix.schemas import (
    AttachedExternalResource,
    AttachedExternalResources,
    CompetencyMatrixItem,
    CompetencyMatrixItemCreateParams,
    CompetencyMatrixItems,
    CompetencyMatrixItemStructure,
    CompetencyMatrixItemUpdateParams,
    ExistingExternalResourceAttachment,
    ExternalResource,
    ExternalResources,
    NewExternalResourceAttachment,
    QueuedCompetencyMatrixQuestion,
    QueuedCompetencyMatrixQuestionCreateParams,
    QueuedCompetencyMatrixQuestions,
    Sheet,
    Sheets,
)
from core.contacts.schemas import ContactMe
from core.enums import PublishStatusEnum
from core.files.schemas import PresignPutObject, PresignPutObjectParams
from core.files.types import Namespace
from core.i18n.enums import LanguageEnum
from core.resumes.enums import ResumeCurrentStatusEnum
from core.resumes.schemas import (
    Resume,
    ResumeAdditionalSection,
    ResumeAdditionalSectionItem,
    ResumeCertificationItem,
    ResumeContent,
    ResumeEducationItem,
    ResumeExperienceItem,
    ResumeLanguageItem,
    ResumeProfile,
    ResumeProjectItem,
    Resumes,
    ResumeSkillGroup,
    ResumeSummary,
)
from core.schemas import Secret
from core.types import IntId, SearchName


class CoreFactoryHelper:
    @staticmethod
    def _fallback(value: str | None, fallback: str) -> str:
        return value if value is not None else fallback

    @classmethod
    def external_resource(
        cls,
        resource_id: Any,
        name: str = "RESOURCE",
        name_ru: str | None = None,
        name_en: str | None = None,
        url: str = "https://example.com",
    ) -> ExternalResource:
        return ExternalResource(
            id=cls.int_id(resource_id) if isinstance(resource_id, int) else resource_id,
            name_ru=name_ru or name,
            name_en=name_en or name,
            url=url,
        )

    @classmethod
    def external_resources(
        cls,
        values: list[ExternalResource] | None = None,
    ) -> ExternalResources:
        return ExternalResources(values=values or [])

    @classmethod
    def attached_external_resource(
        cls,
        resource_id: Any,
        name: str = "RESOURCE",
        name_ru: str | None = None,
        name_en: str | None = None,
        url: str = "https://example.com",
        context: str = "Context",
        context_ru: str | None = None,
        context_en: str | None = None,
    ) -> AttachedExternalResource:
        return AttachedExternalResource(
            id=cls.int_id(resource_id) if isinstance(resource_id, int) else resource_id,
            name_ru=name_ru or name,
            name_en=name_en or name,
            url=url,
            context_ru=context_ru or context,
            context_en=context_en or context,
        )

    @classmethod
    def attached_external_resources(
        cls,
        values: list[AttachedExternalResource] | None = None,
    ) -> AttachedExternalResources:
        return AttachedExternalResources(values=values or [])

    @classmethod
    def existing_external_resource_attachment(
        cls,
        resource_id: Any,
        context: str = "Context",
        context_ru: str | None = None,
        context_en: str | None = None,
    ) -> ExistingExternalResourceAttachment:
        return ExistingExternalResourceAttachment(
            resource_id=cls.int_id(resource_id) if isinstance(resource_id, int) else resource_id,
            context_ru=context_ru or context,
            context_en=context_en or context,
        )

    @classmethod
    def new_external_resource_attachment(
        cls,
        resource_id: Any,
        name: str = "RESOURCE",
        name_ru: str | None = None,
        name_en: str | None = None,
        url: str = "https://example.com",
        context: str = "Context",
        context_ru: str | None = None,
        context_en: str | None = None,
    ) -> NewExternalResourceAttachment:
        return NewExternalResourceAttachment(
            resource=cls.external_resource(
                resource_id=resource_id,
                name=name,
                name_ru=name_ru,
                name_en=name_en,
                url=url,
            ),
            context_ru=context_ru or context,
            context_en=context_en or context,
        )

    @classmethod
    def competency_matrix_item(
        cls,
        item_id: int,
        sheet_id: int = 1,
        section_id: int = 1,
        subsection_id: int = 1,
        slug: str | None = None,
        published_at: str | None = None,
        question: str = "QUESTION",
        question_ru: str | None = None,
        question_en: str | None = None,
        publish_status: PublishStatusEnum = PublishStatusEnum.PUBLISHED,
        answer: str = "Answer",
        answer_ru: str | None = None,
        answer_en: str | None = None,
        interview_expected_answer: str = "Answer",
        interview_expected_answer_ru: str | None = None,
        interview_expected_answer_en: str | None = None,
        sheet_key: str | None = None,
        sheet: str = "Sheet",
        sheet_ru: str | None = None,
        sheet_en: str | None = None,
        grade: GradeEnum | None = GradeEnum.JUNIOR,
        interview_frequency: InterviewFrequencyEnum | None = InterviewFrequencyEnum.OFTEN,
        section: str = "Section",
        section_ru: str | None = None,
        section_en: str | None = None,
        subsection: str = "Subsection",
        subsection_ru: str | None = None,
        subsection_en: str | None = None,
        resources: list[AttachedExternalResource] | None = None,
    ) -> CompetencyMatrixItem:
        question_en_value = cls._fallback(question_en, question)
        return CompetencyMatrixItem(
            id=cls.int_id(item_id),
            slug=cls._fallback(slug, slugify(question_en_value)),
            question_ru=cls._fallback(question_ru, question),
            question_en=question_en_value,
            publish_status=publish_status,
            published_at=(
                datetime.fromisoformat(published_at).replace(tzinfo=UTC)
                if published_at is not None
                else None
            ),
            answer_ru=cls._fallback(answer_ru, answer),
            answer_en=cls._fallback(answer_en, answer),
            interview_expected_answer_ru=cls._fallback(
                interview_expected_answer_ru,
                interview_expected_answer,
            ),
            interview_expected_answer_en=cls._fallback(
                interview_expected_answer_en,
                interview_expected_answer,
            ),
            structure=cls.competency_matrix_item_structure(
                sheet_id=sheet_id,
                section_id=section_id,
                subsection_id=subsection_id,
                sheet_key=cls._fallback(sheet_key, sheet.lower().replace(" ", "-")),
                sheet_ru=cls._fallback(sheet_ru, sheet),
                sheet_en=cls._fallback(sheet_en, sheet),
                section_ru=cls._fallback(section_ru, section),
                section_en=cls._fallback(section_en, section),
                subsection_ru=cls._fallback(subsection_ru, subsection),
                subsection_en=cls._fallback(subsection_en, subsection),
            ),
            grade=grade,
            interview_frequency=interview_frequency,
            resources=AttachedExternalResources(values=resources or []),
        )

    @classmethod
    def competency_matrix_item_structure(
        cls,
        subsection_id: int = 1,
        sheet_id: int = 1,
        sheet_key: str = "sheet",
        sheet_ru: str = "Sheet",
        sheet_en: str = "Sheet",
        section_id: int = 1,
        section_ru: str = "Section",
        section_en: str = "Section",
        subsection_ru: str = "Subsection",
        subsection_en: str = "Subsection",
    ) -> CompetencyMatrixItemStructure:
        return CompetencyMatrixItemStructure(
            sheet_id=cls.int_id(sheet_id),
            sheet_key=sheet_key,
            sheet_ru=sheet_ru,
            sheet_en=sheet_en,
            section_id=cls.int_id(section_id),
            section_ru=section_ru,
            section_en=section_en,
            subsection_id=cls.int_id(subsection_id),
            subsection_ru=subsection_ru,
            subsection_en=subsection_en,
        )

    @classmethod
    def competency_matrix_item_create_params(
        cls,
        item_id: int,
        sheet_id: int = 1,
        section_id: int = 1,
        subsection_id: int = 1,
        slug: str | None = None,
        question: str = "QUESTION",
        question_ru: str | None = None,
        question_en: str | None = None,
        publish_status: PublishStatusEnum = PublishStatusEnum.PUBLISHED,
        answer: str = "Answer",
        answer_ru: str | None = None,
        answer_en: str | None = None,
        interview_expected_answer: str = "Answer",
        interview_expected_answer_ru: str | None = None,
        interview_expected_answer_en: str | None = None,
        sheet_key: str | None = None,
        sheet: str = "Sheet",
        sheet_ru: str | None = None,
        sheet_en: str | None = None,
        grade: GradeEnum | None = GradeEnum.JUNIOR,
        interview_frequency: InterviewFrequencyEnum | None = InterviewFrequencyEnum.OFTEN,
        section: str = "Section",
        section_ru: str | None = None,
        section_en: str | None = None,
        subsection: str = "Subsection",
        subsection_ru: str | None = None,
        subsection_en: str | None = None,
        resources: (
            list[ExistingExternalResourceAttachment | NewExternalResourceAttachment] | None
        ) = None,
    ) -> CompetencyMatrixItemCreateParams:
        _ = (
            sheet_id,
            section_id,
            sheet_key,
            sheet,
            sheet_ru,
            sheet_en,
            section,
            section_ru,
            section_en,
            subsection,
            subsection_ru,
            subsection_en,
        )
        question_en_value = cls._fallback(question_en, question)
        return CompetencyMatrixItemCreateParams(
            id=cls.int_id(item_id),
            slug=cls._fallback(slug, slugify(question_en_value)),
            question_ru=cls._fallback(question_ru, question),
            question_en=question_en_value,
            publish_status=publish_status,
            answer_ru=cls._fallback(answer_ru, answer),
            answer_en=cls._fallback(answer_en, answer),
            interview_expected_answer_ru=cls._fallback(
                interview_expected_answer_ru,
                interview_expected_answer,
            ),
            interview_expected_answer_en=cls._fallback(
                interview_expected_answer_en,
                interview_expected_answer,
            ),
            subsection_id=cls.int_id(subsection_id),
            grade=grade,
            interview_frequency=interview_frequency,
            resources=resources or [],
        )

    @classmethod
    def competency_matrix_item_update_params(
        cls,
        item_id: int,
        sheet_id: int = 1,
        section_id: int = 1,
        subsection_id: int = 1,
        slug: str | None = None,
        question: str = "QUESTION",
        question_ru: str | None = None,
        question_en: str | None = None,
        publish_status: PublishStatusEnum = PublishStatusEnum.PUBLISHED,
        answer: str = "Answer",
        answer_ru: str | None = None,
        answer_en: str | None = None,
        interview_expected_answer: str = "Answer",
        interview_expected_answer_ru: str | None = None,
        interview_expected_answer_en: str | None = None,
        sheet_key: str | None = None,
        sheet: str = "Sheet",
        sheet_ru: str | None = None,
        sheet_en: str | None = None,
        grade: GradeEnum | None = GradeEnum.JUNIOR,
        interview_frequency: InterviewFrequencyEnum | None = InterviewFrequencyEnum.OFTEN,
        section: str = "Section",
        section_ru: str | None = None,
        section_en: str | None = None,
        subsection: str = "Subsection",
        subsection_ru: str | None = None,
        subsection_en: str | None = None,
        resources: (
            list[ExistingExternalResourceAttachment | NewExternalResourceAttachment] | None
        ) = None,
    ) -> CompetencyMatrixItemUpdateParams:
        _ = (
            sheet_id,
            section_id,
            sheet_key,
            sheet,
            sheet_ru,
            sheet_en,
            section,
            section_ru,
            section_en,
            subsection,
            subsection_ru,
            subsection_en,
        )
        question_en_value = cls._fallback(question_en, question)
        return CompetencyMatrixItemUpdateParams(
            id=cls.int_id(item_id),
            slug=cls._fallback(slug, slugify(question_en_value)),
            question_ru=cls._fallback(question_ru, question),
            question_en=question_en_value,
            publish_status=publish_status,
            answer_ru=cls._fallback(answer_ru, answer),
            answer_en=cls._fallback(answer_en, answer),
            interview_expected_answer_ru=cls._fallback(
                interview_expected_answer_ru,
                interview_expected_answer,
            ),
            interview_expected_answer_en=cls._fallback(
                interview_expected_answer_en,
                interview_expected_answer,
            ),
            subsection_id=cls.int_id(subsection_id),
            grade=grade,
            interview_frequency=interview_frequency,
            resources=resources or [],
        )

    @classmethod
    def sheet(
        cls,
        key: str = "python",
        name: str = "Python",
        name_ru: str | None = None,
        name_en: str | None = None,
    ) -> Sheet:
        return Sheet(key=key, name_ru=name_ru or name, name_en=name_en or name)

    @classmethod
    def sheets(cls, values: list[Sheet] | list[str] | None = None) -> Sheets:
        if values is None:
            return Sheets(values=[])
        return Sheets(
            values=[
                cls.sheet(key=value.lower(), name=value) if isinstance(value, str) else value
                for value in values
            ],
        )

    @classmethod
    def queued_competency_matrix_question(
        cls,
        question_id: int,
        question: str = "What is PEP 8?",
        grade: GradeEnum | None = None,
        sheet: str | None = None,
        section: str | None = None,
        subsection: str | None = None,
        suggested_by_username: str | None = None,
        created_at: datetime | None = None,
    ) -> QueuedCompetencyMatrixQuestion:
        return QueuedCompetencyMatrixQuestion(
            id=cls.int_id(question_id),
            question=question,
            grade=grade,
            sheet=sheet,
            section=section,
            subsection=subsection,
            suggested_by_username=suggested_by_username,
            created_at=created_at or datetime.now(tz=UTC),
        )

    @classmethod
    def queued_competency_matrix_questions(
        cls,
        values: list[QueuedCompetencyMatrixQuestion] | None = None,
    ) -> QueuedCompetencyMatrixQuestions:
        return QueuedCompetencyMatrixQuestions(values=values or [])

    @classmethod
    def queued_competency_matrix_question_create_params(
        cls,
        question: str = "What is PEP 8?",
    ) -> QueuedCompetencyMatrixQuestionCreateParams:
        return QueuedCompetencyMatrixQuestionCreateParams(question=question)

    @classmethod
    def user(
        cls,
        username: str = "",
        password_hash: str = "",
        role: RoleEnum = RoleEnum.USER,
    ) -> User:
        return User(username=username, password_hash=Secret(password_hash), role=role)

    @classmethod
    def competency_matrix_items(
        cls,
        values: list[CompetencyMatrixItem] | None = None,
    ) -> CompetencyMatrixItems:
        return CompetencyMatrixItems(values=values or [])

    @classmethod
    def contact_me(
        cls,
        contact_me_id: uuid.UUID | None = None,
        name: str | None = None,
        email: str | None = None,
        telegram: str | None = None,
        message: str = "Message",
    ) -> ContactMe:
        return ContactMe(
            id=contact_me_id or uuid.uuid4(),
            name=name,
            email=email,
            telegram=telegram,
            message=message,
        )

    @classmethod
    def article(
        cls,
        article_id: uuid.UUID | None = None,
        title: str = "Test Article",
        content: str = "This is a test article content.",
        slug: str = "test-articles-article",
        folder: str = "General",
        title_ru: str | None = None,
        title_en: str | None = None,
        content_ru: str | None = None,
        content_en: str | None = None,
        folder_ru: str | None = None,
        folder_en: str | None = None,
        seo_title_ru: str | None = None,
        seo_title_en: str | None = None,
        seo_description_ru: str | None = None,
        seo_description_en: str | None = None,
        cover_image_url: str | None = None,
        cover_image_alt_ru: str | None = None,
        cover_image_alt_en: str | None = None,
        metadata: ArticleMetadata | None = None,
        author_username: str = "admin",
        publish_status: PublishStatusEnum = PublishStatusEnum.PUBLISHED,
        published_at: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        tags: list[Tag] | None = None,
    ) -> Article:
        now = datetime.now(tz=UTC)
        return Article(
            id=article_id or uuid.uuid4(),
            slug=slug,
            title_ru=title_ru or title,
            title_en=title_en or title,
            content_ru=content_ru or content,
            content_en=content_en or content,
            folder_ru=folder_ru or folder,
            folder_en=folder_en or folder,
            author_username=author_username,
            metadata=metadata
            or ArticleMetadata(
                seo_title_ru=seo_title_ru,
                seo_title_en=seo_title_en,
                seo_description_ru=seo_description_ru,
                seo_description_en=seo_description_en,
                cover_image_url=cover_image_url,
                cover_image_alt_ru=cover_image_alt_ru,
                cover_image_alt_en=cover_image_alt_en,
            ),
            publish_status=publish_status,
            published_at=(
                datetime.fromisoformat(published_at).replace(tzinfo=UTC)
                if published_at is not None
                else None
            ),
            created_at=(
                datetime.fromisoformat(created_at).replace(tzinfo=UTC)
                if created_at is not None
                else now
            ),
            updated_at=(
                datetime.fromisoformat(updated_at).replace(tzinfo=UTC)
                if updated_at is not None
                else now
            ),
            tags=Tags(values=tags or []),
        )

    @classmethod
    def article_list(
        cls,
        articles: list[Article] | None = None,
        total_count: int = 0,
        total_pages: int = 0,
    ) -> Articles:
        return Articles(values=articles or [], total_count=total_count, total_pages=total_pages)

    @classmethod
    def tag(
        cls,
        tag_id: IntId | int = 1,
        name: str = "Python",
        name_ru: str | None = None,
        name_en: str | None = None,
        slug: str = "python",
        deleted_at: str | None = None,
    ) -> Tag:
        return Tag(
            id=cls.int_id(tag_id) if isinstance(tag_id, int) else tag_id,
            name_ru=name_ru or name,
            name_en=name_en or name,
            slug=slug,
            deleted_at=(
                datetime.fromisoformat(deleted_at).replace(tzinfo=UTC)
                if deleted_at is not None
                else None
            ),
        )

    @classmethod
    def tags(cls, values: list[Tag] | None = None) -> Tags:
        return Tags(values=values or [])

    @classmethod
    def resume_content(
        cls,
        full_name: str = "Candidate Name",
        role: str = "Инженер",
        summary: str = "Короткое описание опыта.",
        skills: list[ResumeSkillGroup] | None = None,
        experience: list[ResumeExperienceItem] | None = None,
    ) -> ResumeContent:
        return ResumeContent(
            profile=ResumeProfile(
                full_name=full_name,
                role=role,
                location="",
                email="",
                phone="",
                website_url="",
                linkedin_url="",
                github_url="",
                telegram="",
            ),
            summary=ResumeSummary(text=summary),
            skills=skills
            if skills is not None
            else [
                ResumeSkillGroup(
                    category="Backend",
                    items=["Python", "PostgreSQL"],
                ),
            ],
            experience=experience if experience is not None else [],
            education=[],
            languages=[],
            certifications=[],
            additional_sections=[],
        )

    @classmethod
    def resume_empty_content(cls, summary: str = "") -> ResumeContent:
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

    @classmethod
    def resume_full_content(
        cls,
        summary: str = "Builds reliable backend systems.",
        skill_items: list[str] | None = None,
    ) -> ResumeContent:
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
            summary=ResumeSummary(text=summary),
            skills=[
                ResumeSkillGroup(
                    category="Languages",
                    items=skill_items if skill_items is not None else ["Python", "TypeScript"],
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

    @classmethod
    def resume(
        cls,
        resume_id: IntId | int = 1,
        title: str = "Backend resume",
        language: LanguageEnum = LanguageEnum.RU,
        content: ResumeContent | None = None,
        author_username: str = "test",
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> Resume:
        now = datetime.now(tz=UTC)
        return Resume(
            id=cls.int_id(resume_id) if isinstance(resume_id, int) else resume_id,
            title=title,
            language=language,
            content=content or cls.resume_content(),
            author_username=author_username,
            created_at=(
                datetime.fromisoformat(created_at).replace(tzinfo=UTC)
                if created_at is not None
                else now
            ),
            updated_at=(
                datetime.fromisoformat(updated_at).replace(tzinfo=UTC)
                if updated_at is not None
                else now
            ),
        )

    @classmethod
    def resumes(
        cls,
        values: list[Resume] | None = None,
        total_count: int = 0,
        total_pages: int = 0,
    ) -> Resumes:
        return Resumes(values=values or [], total_count=total_count, total_pages=total_pages)

    @classmethod
    def article_reaction_counts(
        cls,
        heart: int = 0,
        fire: int = 0,
        thinking: int = 0,
        neutral: int = 0,
        poop: int = 0,
    ) -> ArticleReactionCounts:
        return ArticleReactionCounts(
            heart=heart,
            fire=fire,
            thinking=thinking,
            neutral=neutral,
            poop=poop,
        )

    @classmethod
    def jwt_user(
        cls,
        username: str = "test",
        role: RoleEnum = RoleEnum.ADMIN,
    ) -> JwtUser:
        return JwtUser(username=username, role=role)

    @classmethod
    def presign_put_object_params(
        cls,
        folder: str = "folder",
        namespace: Namespace = "media",
        content_type: str = "application/octet-stream",
    ) -> PresignPutObjectParams:
        return PresignPutObjectParams(
            folder=folder,
            namespace=namespace,
            content_type=content_type,
        )

    @classmethod
    def presign_put_object(
        cls,
        upload_url: str = "http://localhost/upload_url",
        access_url: str = "http://localhost/access_url",
    ) -> PresignPutObject:
        return PresignPutObject(upload_url=upload_url, access_url=access_url)

    @classmethod
    def token(cls, value: bytes) -> Token:
        return Token(value)

    @classmethod
    def int_id(cls, value: int) -> IntId:
        return IntId(value)

    @classmethod
    def search_name(cls, value: Any) -> SearchName:
        return SearchName(value)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
