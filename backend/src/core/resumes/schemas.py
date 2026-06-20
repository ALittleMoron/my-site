from dataclasses import dataclass
from datetime import date, datetime
from math import ceil
from typing import Self

from core.resumes.enums import ResumeCurrentStatusEnum
from core.schemas import ValuedDataclass
from core.types import IntId


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeProfile:
    full_name: str
    role_ru: str
    role_en: str
    location_ru: str
    location_en: str
    email: str
    phone: str
    website_url: str
    linkedin_url: str
    github_url: str
    telegram: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeSummary:
    text_ru: str
    text_en: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeSkillGroup:
    category_ru: str
    category_en: str
    items: list[str]


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeProjectItem:
    name_ru: str
    name_en: str
    role_ru: str
    role_en: str
    description_ru: str
    description_en: str
    highlights_ru: list[str]
    highlights_en: list[str]
    technologies: list[str]
    url: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeExperienceItem:
    company_ru: str
    company_en: str
    position_ru: str
    position_en: str
    location_ru: str
    location_en: str
    start_date: date | None
    end_date: date | None
    current_status: ResumeCurrentStatusEnum
    summary_ru: str
    summary_en: str
    highlights_ru: list[str]
    highlights_en: list[str]
    technologies: list[str]
    projects: list[ResumeProjectItem]


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeEducationItem:
    institution_ru: str
    institution_en: str
    degree_ru: str
    degree_en: str
    field_ru: str
    field_en: str
    location_ru: str
    location_en: str
    start_date: date | None
    end_date: date | None
    description_ru: str
    description_en: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeLanguageItem:
    name_ru: str
    name_en: str
    proficiency_ru: str
    proficiency_en: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeCertificationItem:
    name_ru: str
    name_en: str
    issuer_ru: str
    issuer_en: str
    issued_on: date | None
    expires_on: date | None
    credential_url: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeAdditionalSectionItem:
    title_ru: str
    title_en: str
    description_ru: str
    description_en: str
    url: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeAdditionalSection:
    title_ru: str
    title_en: str
    items: list[ResumeAdditionalSectionItem]


@dataclass(frozen=True, slots=True, kw_only=True)
class ResumeContent:
    profile: ResumeProfile
    summary: ResumeSummary
    skills: list[ResumeSkillGroup]
    experience: list[ResumeExperienceItem]
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
