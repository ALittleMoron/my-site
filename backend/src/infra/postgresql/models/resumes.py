from datetime import date
from typing import Any, Self

from sqlalchemy import Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_dev_utils.mixins.audit import AuditMixin
from sqlalchemy_dev_utils.mixins.ids import IntegerIDMixin

from core.resumes.enums import ResumeCurrentStatusEnum
from core.resumes.schemas import (
    Resume,
    ResumeAdditionalSection,
    ResumeAdditionalSectionItem,
    ResumeCertificationItem,
    ResumeContent,
    ResumeCreateParams,
    ResumeEducationItem,
    ResumeExperienceItem,
    ResumeLanguageItem,
    ResumeProfile,
    ResumeProjectItem,
    ResumeSkillGroup,
    ResumeSummary,
)
from core.types import IntId
from infra.postgresql.models.base import BaseModel


class ResumeModel(IntegerIDMixin, AuditMixin, BaseModel):
    title: Mapped[str] = mapped_column(String(length=255), doc="Private workspace resume title")
    author_username: Mapped[str] = mapped_column(
        String(length=255),
        doc="Username of the resume author",
    )
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, doc="Structured ATS resume content")

    __table_args__ = (
        Index(
            "resumes_resume_author_updated_id_idx",
            "author_username",
            text("updated_at DESC"),
            text("id DESC"),
        ),
    )

    @classmethod
    def from_create_params(cls, *, params: ResumeCreateParams) -> Self:
        return cls(
            title=params.title,
            author_username=params.author_username,
            content=cls._content_to_json(content=params.content),
        )

    @classmethod
    def from_domain_schema(cls, *, resume: Resume) -> Self:
        return cls(
            id=resume.id,
            title=resume.title,
            author_username=resume.author_username,
            content=cls._content_to_json(content=resume.content),
            created_at=resume.created_at,
            updated_at=resume.updated_at,
        )

    def update_from_domain_schema(self, *, resume: Resume) -> None:
        self.title = resume.title
        self.author_username = resume.author_username
        self.content = self._content_to_json(content=resume.content)
        self.updated_at = resume.updated_at

    def to_domain_schema(self) -> Resume:
        return Resume(
            id=IntId(self.id),
            title=self.title,
            content=self._content_from_json(data=self.content),
            author_username=self.author_username,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def _content_to_json(cls, *, content: ResumeContent) -> dict[str, Any]:
        return {
            "profile": cls._profile_to_json(profile=content.profile),
            "summary": {
                "text_ru": content.summary.text_ru,
                "text_en": content.summary.text_en,
            },
            "skills": [
                {
                    "category_ru": skill.category_ru,
                    "category_en": skill.category_en,
                    "items": list(skill.items),
                }
                for skill in content.skills
            ],
            "experience": [
                cls._experience_to_json(experience=experience) for experience in content.experience
            ],
            "education": [
                cls._education_to_json(education=education) for education in content.education
            ],
            "languages": [
                {
                    "name_ru": language.name_ru,
                    "name_en": language.name_en,
                    "proficiency_ru": language.proficiency_ru,
                    "proficiency_en": language.proficiency_en,
                }
                for language in content.languages
            ],
            "certifications": [
                cls._certification_to_json(certification=certification)
                for certification in content.certifications
            ],
            "additional_sections": [
                cls._additional_section_to_json(section=section)
                for section in content.additional_sections
            ],
        }

    @staticmethod
    def _profile_to_json(*, profile: ResumeProfile) -> dict[str, str]:
        return {
            "full_name": profile.full_name,
            "role_ru": profile.role_ru,
            "role_en": profile.role_en,
            "location_ru": profile.location_ru,
            "location_en": profile.location_en,
            "email": profile.email,
            "phone": profile.phone,
            "website_url": profile.website_url,
            "linkedin_url": profile.linkedin_url,
            "github_url": profile.github_url,
            "telegram": profile.telegram,
        }

    @classmethod
    def _experience_to_json(cls, *, experience: ResumeExperienceItem) -> dict[str, Any]:
        return {
            "company_ru": experience.company_ru,
            "company_en": experience.company_en,
            "position_ru": experience.position_ru,
            "position_en": experience.position_en,
            "location_ru": experience.location_ru,
            "location_en": experience.location_en,
            "start_date": cls._date_to_json(value=experience.start_date),
            "end_date": cls._date_to_json(value=experience.end_date),
            "current_status": cls._current_status_to_json(value=experience.current_status),
            "summary_ru": experience.summary_ru,
            "summary_en": experience.summary_en,
            "highlights_ru": list(experience.highlights_ru),
            "highlights_en": list(experience.highlights_en),
            "technologies": list(experience.technologies),
            "projects": [cls._project_to_json(project=project) for project in experience.projects],
        }

    @staticmethod
    def _project_to_json(*, project: ResumeProjectItem) -> dict[str, Any]:
        return {
            "name_ru": project.name_ru,
            "name_en": project.name_en,
            "role_ru": project.role_ru,
            "role_en": project.role_en,
            "description_ru": project.description_ru,
            "description_en": project.description_en,
            "highlights_ru": list(project.highlights_ru),
            "highlights_en": list(project.highlights_en),
            "technologies": list(project.technologies),
            "url": project.url,
        }

    @classmethod
    def _education_to_json(cls, *, education: ResumeEducationItem) -> dict[str, Any]:
        return {
            "institution_ru": education.institution_ru,
            "institution_en": education.institution_en,
            "degree_ru": education.degree_ru,
            "degree_en": education.degree_en,
            "field_ru": education.field_ru,
            "field_en": education.field_en,
            "location_ru": education.location_ru,
            "location_en": education.location_en,
            "start_date": cls._date_to_json(value=education.start_date),
            "end_date": cls._date_to_json(value=education.end_date),
            "description_ru": education.description_ru,
            "description_en": education.description_en,
        }

    @classmethod
    def _certification_to_json(
        cls,
        *,
        certification: ResumeCertificationItem,
    ) -> dict[str, Any]:
        return {
            "name_ru": certification.name_ru,
            "name_en": certification.name_en,
            "issuer_ru": certification.issuer_ru,
            "issuer_en": certification.issuer_en,
            "issued_on": cls._date_to_json(value=certification.issued_on),
            "expires_on": cls._date_to_json(value=certification.expires_on),
            "credential_url": certification.credential_url,
        }

    @staticmethod
    def _additional_section_to_json(*, section: ResumeAdditionalSection) -> dict[str, Any]:
        return {
            "title_ru": section.title_ru,
            "title_en": section.title_en,
            "items": [
                {
                    "title_ru": item.title_ru,
                    "title_en": item.title_en,
                    "description_ru": item.description_ru,
                    "description_en": item.description_en,
                    "url": item.url,
                }
                for item in section.items
            ],
        }

    @classmethod
    def _content_from_json(cls, *, data: dict[str, Any]) -> ResumeContent:
        return ResumeContent(
            profile=cls._profile_from_json(data=data["profile"]),
            summary=ResumeSummary(
                text_ru=cls._string_from_json(value=data["summary"]["text_ru"]),
                text_en=cls._string_from_json(value=data["summary"]["text_en"]),
            ),
            skills=[
                ResumeSkillGroup(
                    category_ru=cls._string_from_json(value=skill["category_ru"]),
                    category_en=cls._string_from_json(value=skill["category_en"]),
                    items=cls._string_list_from_json(value=skill["items"]),
                )
                for skill in cls._list_from_json(value=data["skills"])
            ],
            experience=[
                cls._experience_from_json(data=experience)
                for experience in cls._list_from_json(value=data["experience"])
            ],
            education=[
                cls._education_from_json(data=education)
                for education in cls._list_from_json(value=data["education"])
            ],
            languages=[
                ResumeLanguageItem(
                    name_ru=cls._string_from_json(value=language["name_ru"]),
                    name_en=cls._string_from_json(value=language["name_en"]),
                    proficiency_ru=cls._string_from_json(value=language["proficiency_ru"]),
                    proficiency_en=cls._string_from_json(value=language["proficiency_en"]),
                )
                for language in cls._list_from_json(value=data["languages"])
            ],
            certifications=[
                cls._certification_from_json(data=certification)
                for certification in cls._list_from_json(value=data["certifications"])
            ],
            additional_sections=[
                cls._additional_section_from_json(data=section)
                for section in cls._list_from_json(value=data["additional_sections"])
            ],
        )

    @classmethod
    def _profile_from_json(cls, *, data: dict[str, Any]) -> ResumeProfile:
        return ResumeProfile(
            full_name=cls._string_from_json(value=data["full_name"]),
            role_ru=cls._string_from_json(value=data["role_ru"]),
            role_en=cls._string_from_json(value=data["role_en"]),
            location_ru=cls._string_from_json(value=data["location_ru"]),
            location_en=cls._string_from_json(value=data["location_en"]),
            email=cls._string_from_json(value=data["email"]),
            phone=cls._string_from_json(value=data["phone"]),
            website_url=cls._string_from_json(value=data["website_url"]),
            linkedin_url=cls._string_from_json(value=data["linkedin_url"]),
            github_url=cls._string_from_json(value=data["github_url"]),
            telegram=cls._string_from_json(value=data["telegram"]),
        )

    @classmethod
    def _experience_from_json(cls, *, data: dict[str, Any]) -> ResumeExperienceItem:
        return ResumeExperienceItem(
            company_ru=cls._string_from_json(value=data["company_ru"]),
            company_en=cls._string_from_json(value=data["company_en"]),
            position_ru=cls._string_from_json(value=data["position_ru"]),
            position_en=cls._string_from_json(value=data["position_en"]),
            location_ru=cls._string_from_json(value=data["location_ru"]),
            location_en=cls._string_from_json(value=data["location_en"]),
            start_date=cls._date_from_json(value=data["start_date"]),
            end_date=cls._date_from_json(value=data["end_date"]),
            current_status=cls._current_status_from_json(data=data),
            summary_ru=cls._string_from_json(value=data["summary_ru"]),
            summary_en=cls._string_from_json(value=data["summary_en"]),
            highlights_ru=cls._string_list_from_json(value=data["highlights_ru"]),
            highlights_en=cls._string_list_from_json(value=data["highlights_en"]),
            technologies=cls._string_list_from_json(value=data["technologies"]),
            projects=[
                cls._project_from_json(data=project)
                for project in cls._list_from_json(value=data["projects"])
            ],
        )

    @classmethod
    def _project_from_json(cls, *, data: dict[str, Any]) -> ResumeProjectItem:
        return ResumeProjectItem(
            name_ru=cls._string_from_json(value=data["name_ru"]),
            name_en=cls._string_from_json(value=data["name_en"]),
            role_ru=cls._string_from_json(value=data["role_ru"]),
            role_en=cls._string_from_json(value=data["role_en"]),
            description_ru=cls._string_from_json(value=data["description_ru"]),
            description_en=cls._string_from_json(value=data["description_en"]),
            highlights_ru=cls._string_list_from_json(value=data["highlights_ru"]),
            highlights_en=cls._string_list_from_json(value=data["highlights_en"]),
            technologies=cls._string_list_from_json(value=data["technologies"]),
            url=cls._string_from_json(value=data["url"]),
        )

    @classmethod
    def _education_from_json(cls, *, data: dict[str, Any]) -> ResumeEducationItem:
        return ResumeEducationItem(
            institution_ru=cls._string_from_json(value=data["institution_ru"]),
            institution_en=cls._string_from_json(value=data["institution_en"]),
            degree_ru=cls._string_from_json(value=data["degree_ru"]),
            degree_en=cls._string_from_json(value=data["degree_en"]),
            field_ru=cls._string_from_json(value=data["field_ru"]),
            field_en=cls._string_from_json(value=data["field_en"]),
            location_ru=cls._string_from_json(value=data["location_ru"]),
            location_en=cls._string_from_json(value=data["location_en"]),
            start_date=cls._date_from_json(value=data["start_date"]),
            end_date=cls._date_from_json(value=data["end_date"]),
            description_ru=cls._string_from_json(value=data["description_ru"]),
            description_en=cls._string_from_json(value=data["description_en"]),
        )

    @classmethod
    def _certification_from_json(cls, *, data: dict[str, Any]) -> ResumeCertificationItem:
        return ResumeCertificationItem(
            name_ru=cls._string_from_json(value=data["name_ru"]),
            name_en=cls._string_from_json(value=data["name_en"]),
            issuer_ru=cls._string_from_json(value=data["issuer_ru"]),
            issuer_en=cls._string_from_json(value=data["issuer_en"]),
            issued_on=cls._date_from_json(value=data["issued_on"]),
            expires_on=cls._date_from_json(value=data["expires_on"]),
            credential_url=cls._string_from_json(value=data["credential_url"]),
        )

    @classmethod
    def _additional_section_from_json(cls, *, data: dict[str, Any]) -> ResumeAdditionalSection:
        return ResumeAdditionalSection(
            title_ru=cls._string_from_json(value=data["title_ru"]),
            title_en=cls._string_from_json(value=data["title_en"]),
            items=[
                ResumeAdditionalSectionItem(
                    title_ru=cls._string_from_json(value=item["title_ru"]),
                    title_en=cls._string_from_json(value=item["title_en"]),
                    description_ru=cls._string_from_json(value=item["description_ru"]),
                    description_en=cls._string_from_json(value=item["description_en"]),
                    url=cls._string_from_json(value=item["url"]),
                )
                for item in cls._list_from_json(value=data["items"])
            ],
        )

    @staticmethod
    def _string_from_json(*, value: object) -> str:
        return value if isinstance(value, str) else ""

    @staticmethod
    def _list_from_json(*, value: object) -> list[Any]:
        return value if isinstance(value, list) else []

    @classmethod
    def _string_list_from_json(cls, *, value: object) -> list[str]:
        return [cls._string_from_json(value=item) for item in cls._list_from_json(value=value)]

    @staticmethod
    def _current_status_to_json(*, value: ResumeCurrentStatusEnum) -> str:
        return value.value

    @staticmethod
    def _current_status_from_json(*, data: dict[str, Any]) -> ResumeCurrentStatusEnum:
        if "current_status" in data:
            value = data["current_status"]
            if isinstance(value, str):
                try:
                    return ResumeCurrentStatusEnum(value)
                except ValueError:
                    return ResumeCurrentStatusEnum.NOT_SET
            return ResumeCurrentStatusEnum.NOT_SET
        if data.get("is_current") is True:
            return ResumeCurrentStatusEnum.CURRENT
        if data.get("is_current") is False:
            return ResumeCurrentStatusEnum.NOT_CURRENT
        return ResumeCurrentStatusEnum.NOT_SET

    @staticmethod
    def _date_to_json(*, value: date | None) -> str | None:
        return value.isoformat() if value is not None else None

    @staticmethod
    def _date_from_json(*, value: str | None) -> date | None:
        return date.fromisoformat(value) if value is not None else None
