from datetime import date
from typing import Annotated, Self

from pydantic import Field

from core.i18n.enums import LanguageEnum
from core.resumes.enums import ResumeCurrentStatusEnum, ResumeExportFormatEnum
from core.resumes.schemas import (
    Resume,
    ResumeAdditionalSection,
    ResumeAdditionalSectionItem,
    ResumeCertificationItem,
    ResumeContent,
    ResumeCreateParams,
    ResumeEducationItem,
    ResumeExperienceItem,
    ResumeExportParams,
    ResumeLanguageItem,
    ResumeProfile,
    ResumeProjectItem,
    Resumes,
    ResumeSkillGroup,
    ResumeSummary,
    ResumeUpdateParams,
)
from entrypoints.litestar.api.schemas import CamelCaseSchema


class ResumeProfileSchema(CamelCaseSchema):
    full_name: Annotated[str, Field(title="Full name", max_length=255)]
    role: Annotated[str, Field(title="Role", max_length=255)]
    location: Annotated[str, Field(title="Location", max_length=255)]
    email: Annotated[str, Field(title="Email", max_length=255)]
    phone: Annotated[str, Field(title="Phone", max_length=64)]
    website_url: Annotated[str, Field(title="Website URL", max_length=2048)]
    linkedin_url: Annotated[str, Field(title="LinkedIn URL", max_length=2048)]
    github_url: Annotated[str, Field(title="GitHub URL", max_length=2048)]
    telegram: Annotated[str, Field(title="Telegram", max_length=255)]

    def to_domain_schema(self) -> ResumeProfile:
        return ResumeProfile(
            full_name=self.full_name,
            role=self.role,
            location=self.location,
            email=self.email,
            phone=self.phone,
            website_url=self.website_url,
            linkedin_url=self.linkedin_url,
            github_url=self.github_url,
            telegram=self.telegram,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeProfile) -> Self:
        return cls(
            full_name=schema.full_name,
            role=schema.role,
            location=schema.location,
            email=schema.email,
            phone=schema.phone,
            website_url=schema.website_url,
            linkedin_url=schema.linkedin_url,
            github_url=schema.github_url,
            telegram=schema.telegram,
        )


class ResumeSummarySchema(CamelCaseSchema):
    text: Annotated[str, Field(title="Summary")]

    def to_domain_schema(self) -> ResumeSummary:
        return ResumeSummary(text=self.text)

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeSummary) -> Self:
        return cls(text=schema.text)


class ResumeSkillGroupSchema(CamelCaseSchema):
    category: Annotated[str, Field(title="Skill category", max_length=255)]
    items: Annotated[list[str], Field(title="Skill items")]

    def to_domain_schema(self) -> ResumeSkillGroup:
        return ResumeSkillGroup(
            category=self.category,
            items=list(self.items),
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeSkillGroup) -> Self:
        return cls(
            category=schema.category,
            items=list(schema.items),
        )


class ResumeProjectItemSchema(CamelCaseSchema):
    name: Annotated[str, Field(title="Project name", max_length=255)]
    role: Annotated[str, Field(title="Project role", max_length=255)]
    description: Annotated[str, Field(title="Project description")]
    highlights: Annotated[list[str], Field(title="Highlights")]
    technologies: Annotated[list[str], Field(title="Technologies")]
    url: Annotated[str, Field(title="Project URL", max_length=2048)]

    def to_domain_schema(self) -> ResumeProjectItem:
        return ResumeProjectItem(
            name=self.name,
            role=self.role,
            description=self.description,
            highlights=list(self.highlights),
            technologies=list(self.technologies),
            url=self.url,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeProjectItem) -> Self:
        return cls(
            name=schema.name,
            role=schema.role,
            description=schema.description,
            highlights=list(schema.highlights),
            technologies=list(schema.technologies),
            url=schema.url,
        )


class ResumeExperienceItemSchema(CamelCaseSchema):
    company: Annotated[str, Field(title="Company", max_length=255)]
    position: Annotated[str, Field(title="Position", max_length=255)]
    location: Annotated[str, Field(title="Location", max_length=255)]
    start_date: Annotated[date | None, Field(title="Start date")]
    end_date: Annotated[date | None, Field(title="End date")]
    current_status: Annotated[ResumeCurrentStatusEnum, Field(title="Current status")]
    summary: Annotated[str, Field(title="Experience summary")]
    highlights: Annotated[list[str], Field(title="Highlights")]
    technologies: Annotated[list[str], Field(title="Technologies")]
    projects: Annotated[list[ResumeProjectItemSchema], Field(title="Experience projects")]

    def to_domain_schema(self) -> ResumeExperienceItem:
        return ResumeExperienceItem(
            company=self.company,
            position=self.position,
            location=self.location,
            start_date=self.start_date,
            end_date=self.end_date,
            current_status=self.current_status,
            summary=self.summary,
            highlights=list(self.highlights),
            technologies=list(self.technologies),
            projects=[project.to_domain_schema() for project in self.projects],
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeExperienceItem) -> Self:
        return cls(
            company=schema.company,
            position=schema.position,
            location=schema.location,
            start_date=schema.start_date,
            end_date=schema.end_date,
            current_status=schema.current_status,
            summary=schema.summary,
            highlights=list(schema.highlights),
            technologies=list(schema.technologies),
            projects=[
                ResumeProjectItemSchema.from_domain_schema(schema=project)
                for project in schema.projects
            ],
        )


class ResumeEducationItemSchema(CamelCaseSchema):
    institution: Annotated[str, Field(title="Institution", max_length=255)]
    degree: Annotated[str, Field(title="Degree", max_length=255)]
    field: Annotated[str, Field(title="Field", max_length=255)]
    location: Annotated[str, Field(title="Location", max_length=255)]
    start_date: Annotated[date | None, Field(title="Start date")]
    end_date: Annotated[date | None, Field(title="End date")]
    description: Annotated[str, Field(title="Description")]

    def to_domain_schema(self) -> ResumeEducationItem:
        return ResumeEducationItem(
            institution=self.institution,
            degree=self.degree,
            field=self.field,
            location=self.location,
            start_date=self.start_date,
            end_date=self.end_date,
            description=self.description,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeEducationItem) -> Self:
        return cls(
            institution=schema.institution,
            degree=schema.degree,
            field=schema.field,
            location=schema.location,
            start_date=schema.start_date,
            end_date=schema.end_date,
            description=schema.description,
        )


class ResumeLanguageItemSchema(CamelCaseSchema):
    name: Annotated[str, Field(title="Language", max_length=255)]
    proficiency: Annotated[str, Field(title="Proficiency", max_length=255)]

    def to_domain_schema(self) -> ResumeLanguageItem:
        return ResumeLanguageItem(
            name=self.name,
            proficiency=self.proficiency,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeLanguageItem) -> Self:
        return cls(
            name=schema.name,
            proficiency=schema.proficiency,
        )


class ResumeCertificationItemSchema(CamelCaseSchema):
    name: Annotated[str, Field(title="Certification", max_length=255)]
    issuer: Annotated[str, Field(title="Issuer", max_length=255)]
    issued_on: Annotated[date | None, Field(title="Issued on")]
    expires_on: Annotated[date | None, Field(title="Expires on")]
    credential_url: Annotated[str, Field(title="Credential URL", max_length=2048)]

    def to_domain_schema(self) -> ResumeCertificationItem:
        return ResumeCertificationItem(
            name=self.name,
            issuer=self.issuer,
            issued_on=self.issued_on,
            expires_on=self.expires_on,
            credential_url=self.credential_url,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeCertificationItem) -> Self:
        return cls(
            name=schema.name,
            issuer=schema.issuer,
            issued_on=schema.issued_on,
            expires_on=schema.expires_on,
            credential_url=schema.credential_url,
        )


class ResumeAdditionalSectionItemSchema(CamelCaseSchema):
    title: Annotated[str, Field(title="Title", max_length=255)]
    description: Annotated[str, Field(title="Description")]
    url: Annotated[str, Field(title="URL", max_length=2048)]

    def to_domain_schema(self) -> ResumeAdditionalSectionItem:
        return ResumeAdditionalSectionItem(
            title=self.title,
            description=self.description,
            url=self.url,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeAdditionalSectionItem) -> Self:
        return cls(
            title=schema.title,
            description=schema.description,
            url=schema.url,
        )


class ResumeAdditionalSectionSchema(CamelCaseSchema):
    title: Annotated[str, Field(title="Section title", max_length=255)]
    items: Annotated[list[ResumeAdditionalSectionItemSchema], Field(title="Section items")]

    def to_domain_schema(self) -> ResumeAdditionalSection:
        return ResumeAdditionalSection(
            title=self.title,
            items=[item.to_domain_schema() for item in self.items],
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeAdditionalSection) -> Self:
        return cls(
            title=schema.title,
            items=[
                ResumeAdditionalSectionItemSchema.from_domain_schema(schema=item)
                for item in schema.items
            ],
        )


class ResumeContentSchema(CamelCaseSchema):
    profile: Annotated[ResumeProfileSchema, Field(title="Profile")]
    summary: Annotated[ResumeSummarySchema, Field(title="Summary")]
    skills: Annotated[list[ResumeSkillGroupSchema], Field(title="Skills")]
    experience: Annotated[list[ResumeExperienceItemSchema], Field(title="Experience")]
    education: Annotated[list[ResumeEducationItemSchema], Field(title="Education")]
    languages: Annotated[list[ResumeLanguageItemSchema], Field(title="Languages")]
    certifications: Annotated[list[ResumeCertificationItemSchema], Field(title="Certifications")]
    additional_sections: Annotated[
        list[ResumeAdditionalSectionSchema],
        Field(title="Additional sections"),
    ]

    def to_domain_schema(self) -> ResumeContent:
        return ResumeContent(
            profile=self.profile.to_domain_schema(),
            summary=self.summary.to_domain_schema(),
            skills=[skill.to_domain_schema() for skill in self.skills],
            experience=[experience.to_domain_schema() for experience in self.experience],
            education=[education.to_domain_schema() for education in self.education],
            languages=[language.to_domain_schema() for language in self.languages],
            certifications=[
                certification.to_domain_schema() for certification in self.certifications
            ],
            additional_sections=[
                section.to_domain_schema() for section in self.additional_sections
            ],
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeContent) -> Self:
        return cls(
            profile=ResumeProfileSchema.from_domain_schema(schema=schema.profile),
            summary=ResumeSummarySchema.from_domain_schema(schema=schema.summary),
            skills=[
                ResumeSkillGroupSchema.from_domain_schema(schema=skill) for skill in schema.skills
            ],
            experience=[
                ResumeExperienceItemSchema.from_domain_schema(schema=experience)
                for experience in schema.experience
            ],
            education=[
                ResumeEducationItemSchema.from_domain_schema(schema=education)
                for education in schema.education
            ],
            languages=[
                ResumeLanguageItemSchema.from_domain_schema(schema=language)
                for language in schema.languages
            ],
            certifications=[
                ResumeCertificationItemSchema.from_domain_schema(schema=certification)
                for certification in schema.certifications
            ],
            additional_sections=[
                ResumeAdditionalSectionSchema.from_domain_schema(schema=section)
                for section in schema.additional_sections
            ],
        )


class ResumeRequestSchema(CamelCaseSchema):
    title: Annotated[str, Field(title="Workspace title", min_length=1, max_length=255)]
    language: Annotated[LanguageEnum, Field(title="Resume language")]
    content: Annotated[ResumeContentSchema, Field(title="Resume content")]

    def to_create_schema(self, *, author_username: str) -> ResumeCreateParams:
        return ResumeCreateParams(
            title=self.title,
            language=self.language,
            content=self.content.to_domain_schema(),
            author_username=author_username,
        )

    def to_update_schema(self) -> ResumeUpdateParams:
        return ResumeUpdateParams(
            title=self.title,
            language=self.language,
            content=self.content.to_domain_schema(),
        )


class ResumeExportRequestSchema(ResumeRequestSchema):
    format: Annotated[ResumeExportFormatEnum, Field(title="Export format")]

    def to_export_schema(self) -> ResumeExportParams:
        return ResumeExportParams(
            format=self.format,
            title=self.title,
            language=self.language,
            content=self.content.to_domain_schema(),
        )


class ResumeResponseSchema(CamelCaseSchema):
    id: Annotated[int, Field(title="Identifier")]
    title: Annotated[str, Field(title="Workspace title")]
    language: Annotated[LanguageEnum, Field(title="Resume language")]
    content: Annotated[ResumeContentSchema, Field(title="Resume content")]
    created_at: Annotated[str, Field(title="Created at")]
    updated_at: Annotated[str, Field(title="Updated at")]

    @classmethod
    def from_domain_schema(cls, *, schema: Resume) -> Self:
        return cls(
            id=schema.id,
            title=schema.title,
            language=schema.language,
            content=ResumeContentSchema.from_domain_schema(schema=schema.content),
            created_at=schema.created_at.isoformat(),
            updated_at=schema.updated_at.isoformat(),
        )


class ResumesResponseSchema(CamelCaseSchema):
    total_count: Annotated[int, Field(title="Total count")]
    total_pages: Annotated[int, Field(title="Total pages")]
    resumes: Annotated[list[ResumeResponseSchema], Field(title="Resumes")]

    @classmethod
    def from_domain_schema(cls, *, schema: Resumes) -> Self:
        return cls(
            total_count=schema.total_count,
            total_pages=schema.total_pages,
            resumes=[
                ResumeResponseSchema.from_domain_schema(schema=resume) for resume in schema.values
            ],
        )
