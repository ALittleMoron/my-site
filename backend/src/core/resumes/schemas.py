from dataclasses import dataclass
from datetime import date, datetime
from math import ceil
from typing import Self

from core.schemas import ValuedDataclass
from core.types import IntId


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeProfile:
    full_name: str | None
    role_ru: str | None
    role_en: str | None
    location_ru: str | None
    location_en: str | None
    email: str | None
    phone: str | None
    website_url: str | None
    linkedin_url: str | None
    github_url: str | None
    telegram: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeSummary:
    text_ru: str | None
    text_en: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeSkillGroup:
    category_ru: str | None
    category_en: str | None
    items: list[str]


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeExperienceItem:
    company_ru: str | None
    company_en: str | None
    position_ru: str | None
    position_en: str | None
    location_ru: str | None
    location_en: str | None
    start_date: date | None
    end_date: date | None
    is_current: bool | None
    summary_ru: str | None
    summary_en: str | None
    highlights_ru: list[str]
    highlights_en: list[str]
    technologies: list[str]


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeProjectItem:
    name_ru: str | None
    name_en: str | None
    role_ru: str | None
    role_en: str | None
    description_ru: str | None
    description_en: str | None
    highlights_ru: list[str]
    highlights_en: list[str]
    technologies: list[str]
    url: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeEducationItem:
    institution_ru: str | None
    institution_en: str | None
    degree_ru: str | None
    degree_en: str | None
    field_ru: str | None
    field_en: str | None
    location_ru: str | None
    location_en: str | None
    start_date: date | None
    end_date: date | None
    description_ru: str | None
    description_en: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeLanguageItem:
    name_ru: str | None
    name_en: str | None
    proficiency_ru: str | None
    proficiency_en: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeCertificationItem:
    name_ru: str | None
    name_en: str | None
    issuer_ru: str | None
    issuer_en: str | None
    issued_on: date | None
    expires_on: date | None
    credential_url: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeAdditionalSectionItem:
    title_ru: str | None
    title_en: str | None
    description_ru: str | None
    description_en: str | None
    url: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeAdditionalSection:
    title_ru: str | None
    title_en: str | None
    items: list[ResumeAdditionalSectionItem]


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeContent:
    profile: ResumeProfile
    summary: ResumeSummary
    skills: list[ResumeSkillGroup]
    experience: list[ResumeExperienceItem]
    projects: list[ResumeProjectItem]
    education: list[ResumeEducationItem]
    languages: list[ResumeLanguageItem]
    certifications: list[ResumeCertificationItem]
    additional_sections: list[ResumeAdditionalSection]


@dataclass(frozen=True, slots=True, kw_only=True)
class Resume:
    id: IntId
    title: str
    content: ResumeContent
    author_username: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class Resumes(ValuedDataclass[Resume]):
    total_count: int
    total_pages: int

    @classmethod
    def from_page(cls, *, values: list[Resume], total_count: int, page_size: int) -> Self:
        return cls(
            values=values,
            total_count=total_count,
            total_pages=ceil(total_count / page_size) if total_count > 0 else 0,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeFilters:
    page: int | None
    page_size: int | None
    search_query: str | None
    author_username: str

    @property
    def limit(self) -> int:
        if self.page_size is None:
            raise ValueError
        return self.page_size

    @property
    def offset(self) -> int:
        if self.page is None or self.page_size is None:
            raise ValueError
        return (self.page - 1) * self.page_size


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeCreateParams:
    title: str
    content: ResumeContent
    author_username: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeUpdateParams:
    title: str
    content: ResumeContent

    def to_resume(self, *, existing_resume: Resume, now: datetime) -> Resume:
        return Resume(
            id=existing_resume.id,
            title=self.title,
            content=self.content,
            author_username=existing_resume.author_username,
            created_at=existing_resume.created_at,
            updated_at=now,
        )
