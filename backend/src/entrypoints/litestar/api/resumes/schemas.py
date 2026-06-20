from datetime import date
from typing import Annotated, Self

from pydantic import Field

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
    Resumes,
    ResumeSkillGroup,
    ResumeSummary,
    ResumeUpdateParams,
)
from entrypoints.litestar.api.schemas import CamelCaseSchema


class ResumeProfileSchema(CamelCaseSchema):
    full_name: Annotated[str | None, Field(title="Full name", max_length=255)]
    role_ru: Annotated[str | None, Field(title="Role RU", max_length=255)]
    role_en: Annotated[str | None, Field(title="Role EN", max_length=255)]
    location_ru: Annotated[str | None, Field(title="Location RU", max_length=255)]
    location_en: Annotated[str | None, Field(title="Location EN", max_length=255)]
    email: Annotated[str | None, Field(title="Email", max_length=255)]
    phone: Annotated[str | None, Field(title="Phone", max_length=64)]
    website_url: Annotated[str | None, Field(title="Website URL", max_length=2048)]
    linkedin_url: Annotated[str | None, Field(title="LinkedIn URL", max_length=2048)]
    github_url: Annotated[str | None, Field(title="GitHub URL", max_length=2048)]
    telegram: Annotated[str | None, Field(title="Telegram", max_length=255)]

    def to_domain_schema(self) -> ResumeProfile:
        return ResumeProfile(
            full_name=self.full_name,
            role_ru=self.role_ru,
            role_en=self.role_en,
            location_ru=self.location_ru,
            location_en=self.location_en,
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
            role_ru=schema.role_ru,
            role_en=schema.role_en,
            location_ru=schema.location_ru,
            location_en=schema.location_en,
            email=schema.email,
            phone=schema.phone,
            website_url=schema.website_url,
            linkedin_url=schema.linkedin_url,
            github_url=schema.github_url,
            telegram=schema.telegram,
        )


class ResumeSummarySchema(CamelCaseSchema):
    text_ru: Annotated[str | None, Field(title="Summary RU")]
    text_en: Annotated[str | None, Field(title="Summary EN")]

    def to_domain_schema(self) -> ResumeSummary:
        return ResumeSummary(text_ru=self.text_ru, text_en=self.text_en)

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeSummary) -> Self:
        return cls(text_ru=schema.text_ru, text_en=schema.text_en)


class ResumeSkillGroupSchema(CamelCaseSchema):
    category_ru: Annotated[str | None, Field(title="Skill category RU", max_length=255)]
    category_en: Annotated[str | None, Field(title="Skill category EN", max_length=255)]
    items: Annotated[list[str], Field(title="Skill items")]

    def to_domain_schema(self) -> ResumeSkillGroup:
        return ResumeSkillGroup(
            category_ru=self.category_ru,
            category_en=self.category_en,
            items=list(self.items),
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeSkillGroup) -> Self:
        return cls(
            category_ru=schema.category_ru,
            category_en=schema.category_en,
            items=list(schema.items),
        )


class ResumeExperienceItemSchema(CamelCaseSchema):
    company_ru: Annotated[str | None, Field(title="Company RU", max_length=255)]
    company_en: Annotated[str | None, Field(title="Company EN", max_length=255)]
    position_ru: Annotated[str | None, Field(title="Position RU", max_length=255)]
    position_en: Annotated[str | None, Field(title="Position EN", max_length=255)]
    location_ru: Annotated[str | None, Field(title="Location RU", max_length=255)]
    location_en: Annotated[str | None, Field(title="Location EN", max_length=255)]
    start_date: Annotated[date | None, Field(title="Start date")]
    end_date: Annotated[date | None, Field(title="End date")]
    is_current: Annotated[bool | None, Field(title="Current role")]
    summary_ru: Annotated[str | None, Field(title="Experience summary RU")]
    summary_en: Annotated[str | None, Field(title="Experience summary EN")]
    highlights_ru: Annotated[list[str], Field(title="Highlights RU")]
    highlights_en: Annotated[list[str], Field(title="Highlights EN")]
    technologies: Annotated[list[str], Field(title="Technologies")]

    def to_domain_schema(self) -> ResumeExperienceItem:
        return ResumeExperienceItem(
            company_ru=self.company_ru,
            company_en=self.company_en,
            position_ru=self.position_ru,
            position_en=self.position_en,
            location_ru=self.location_ru,
            location_en=self.location_en,
            start_date=self.start_date,
            end_date=self.end_date,
            is_current=self.is_current,
            summary_ru=self.summary_ru,
            summary_en=self.summary_en,
            highlights_ru=list(self.highlights_ru),
            highlights_en=list(self.highlights_en),
            technologies=list(self.technologies),
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeExperienceItem) -> Self:
        return cls(
            company_ru=schema.company_ru,
            company_en=schema.company_en,
            position_ru=schema.position_ru,
            position_en=schema.position_en,
            location_ru=schema.location_ru,
            location_en=schema.location_en,
            start_date=schema.start_date,
            end_date=schema.end_date,
            is_current=schema.is_current,
            summary_ru=schema.summary_ru,
            summary_en=schema.summary_en,
            highlights_ru=list(schema.highlights_ru),
            highlights_en=list(schema.highlights_en),
            technologies=list(schema.technologies),
        )


class ResumeProjectItemSchema(CamelCaseSchema):
    name_ru: Annotated[str | None, Field(title="Project name RU", max_length=255)]
    name_en: Annotated[str | None, Field(title="Project name EN", max_length=255)]
    role_ru: Annotated[str | None, Field(title="Project role RU", max_length=255)]
    role_en: Annotated[str | None, Field(title="Project role EN", max_length=255)]
    description_ru: Annotated[str | None, Field(title="Project description RU")]
    description_en: Annotated[str | None, Field(title="Project description EN")]
    highlights_ru: Annotated[list[str], Field(title="Highlights RU")]
    highlights_en: Annotated[list[str], Field(title="Highlights EN")]
    technologies: Annotated[list[str], Field(title="Technologies")]
    url: Annotated[str | None, Field(title="Project URL", max_length=2048)]

    def to_domain_schema(self) -> ResumeProjectItem:
        return ResumeProjectItem(
            name_ru=self.name_ru,
            name_en=self.name_en,
            role_ru=self.role_ru,
            role_en=self.role_en,
            description_ru=self.description_ru,
            description_en=self.description_en,
            highlights_ru=list(self.highlights_ru),
            highlights_en=list(self.highlights_en),
            technologies=list(self.technologies),
            url=self.url,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeProjectItem) -> Self:
        return cls(
            name_ru=schema.name_ru,
            name_en=schema.name_en,
            role_ru=schema.role_ru,
            role_en=schema.role_en,
            description_ru=schema.description_ru,
            description_en=schema.description_en,
            highlights_ru=list(schema.highlights_ru),
            highlights_en=list(schema.highlights_en),
            technologies=list(schema.technologies),
            url=schema.url,
        )


class ResumeEducationItemSchema(CamelCaseSchema):
    institution_ru: Annotated[str | None, Field(title="Institution RU", max_length=255)]
    institution_en: Annotated[str | None, Field(title="Institution EN", max_length=255)]
    degree_ru: Annotated[str | None, Field(title="Degree RU", max_length=255)]
    degree_en: Annotated[str | None, Field(title="Degree EN", max_length=255)]
    field_ru: Annotated[str | None, Field(title="Field RU", max_length=255)]
    field_en: Annotated[str | None, Field(title="Field EN", max_length=255)]
    location_ru: Annotated[str | None, Field(title="Location RU", max_length=255)]
    location_en: Annotated[str | None, Field(title="Location EN", max_length=255)]
    start_date: Annotated[date | None, Field(title="Start date")]
    end_date: Annotated[date | None, Field(title="End date")]
    description_ru: Annotated[str | None, Field(title="Description RU")]
    description_en: Annotated[str | None, Field(title="Description EN")]

    def to_domain_schema(self) -> ResumeEducationItem:
        return ResumeEducationItem(
            institution_ru=self.institution_ru,
            institution_en=self.institution_en,
            degree_ru=self.degree_ru,
            degree_en=self.degree_en,
            field_ru=self.field_ru,
            field_en=self.field_en,
            location_ru=self.location_ru,
            location_en=self.location_en,
            start_date=self.start_date,
            end_date=self.end_date,
            description_ru=self.description_ru,
            description_en=self.description_en,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeEducationItem) -> Self:
        return cls(
            institution_ru=schema.institution_ru,
            institution_en=schema.institution_en,
            degree_ru=schema.degree_ru,
            degree_en=schema.degree_en,
            field_ru=schema.field_ru,
            field_en=schema.field_en,
            location_ru=schema.location_ru,
            location_en=schema.location_en,
            start_date=schema.start_date,
            end_date=schema.end_date,
            description_ru=schema.description_ru,
            description_en=schema.description_en,
        )


class ResumeLanguageItemSchema(CamelCaseSchema):
    name_ru: Annotated[str | None, Field(title="Language RU", max_length=255)]
    name_en: Annotated[str | None, Field(title="Language EN", max_length=255)]
    proficiency_ru: Annotated[str | None, Field(title="Proficiency RU", max_length=255)]
    proficiency_en: Annotated[str | None, Field(title="Proficiency EN", max_length=255)]

    def to_domain_schema(self) -> ResumeLanguageItem:
        return ResumeLanguageItem(
            name_ru=self.name_ru,
            name_en=self.name_en,
            proficiency_ru=self.proficiency_ru,
            proficiency_en=self.proficiency_en,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeLanguageItem) -> Self:
        return cls(
            name_ru=schema.name_ru,
            name_en=schema.name_en,
            proficiency_ru=schema.proficiency_ru,
            proficiency_en=schema.proficiency_en,
        )


class ResumeCertificationItemSchema(CamelCaseSchema):
    name_ru: Annotated[str | None, Field(title="Certification RU", max_length=255)]
    name_en: Annotated[str | None, Field(title="Certification EN", max_length=255)]
    issuer_ru: Annotated[str | None, Field(title="Issuer RU", max_length=255)]
    issuer_en: Annotated[str | None, Field(title="Issuer EN", max_length=255)]
    issued_on: Annotated[date | None, Field(title="Issued on")]
    expires_on: Annotated[date | None, Field(title="Expires on")]
    credential_url: Annotated[str | None, Field(title="Credential URL", max_length=2048)]

    def to_domain_schema(self) -> ResumeCertificationItem:
        return ResumeCertificationItem(
            name_ru=self.name_ru,
            name_en=self.name_en,
            issuer_ru=self.issuer_ru,
            issuer_en=self.issuer_en,
            issued_on=self.issued_on,
            expires_on=self.expires_on,
            credential_url=self.credential_url,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeCertificationItem) -> Self:
        return cls(
            name_ru=schema.name_ru,
            name_en=schema.name_en,
            issuer_ru=schema.issuer_ru,
            issuer_en=schema.issuer_en,
            issued_on=schema.issued_on,
            expires_on=schema.expires_on,
            credential_url=schema.credential_url,
        )


class ResumeAdditionalSectionItemSchema(CamelCaseSchema):
    title_ru: Annotated[str | None, Field(title="Title RU", max_length=255)]
    title_en: Annotated[str | None, Field(title="Title EN", max_length=255)]
    description_ru: Annotated[str | None, Field(title="Description RU")]
    description_en: Annotated[str | None, Field(title="Description EN")]
    url: Annotated[str | None, Field(title="URL", max_length=2048)]

    def to_domain_schema(self) -> ResumeAdditionalSectionItem:
        return ResumeAdditionalSectionItem(
            title_ru=self.title_ru,
            title_en=self.title_en,
            description_ru=self.description_ru,
            description_en=self.description_en,
            url=self.url,
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeAdditionalSectionItem) -> Self:
        return cls(
            title_ru=schema.title_ru,
            title_en=schema.title_en,
            description_ru=schema.description_ru,
            description_en=schema.description_en,
            url=schema.url,
        )


class ResumeAdditionalSectionSchema(CamelCaseSchema):
    title_ru: Annotated[str | None, Field(title="Section title RU", max_length=255)]
    title_en: Annotated[str | None, Field(title="Section title EN", max_length=255)]
    items: Annotated[list[ResumeAdditionalSectionItemSchema], Field(title="Section items")]

    def to_domain_schema(self) -> ResumeAdditionalSection:
        return ResumeAdditionalSection(
            title_ru=self.title_ru,
            title_en=self.title_en,
            items=[item.to_domain_schema() for item in self.items],
        )

    @classmethod
    def from_domain_schema(cls, *, schema: ResumeAdditionalSection) -> Self:
        return cls(
            title_ru=schema.title_ru,
            title_en=schema.title_en,
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
    projects: Annotated[list[ResumeProjectItemSchema], Field(title="Projects")]
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
            projects=[project.to_domain_schema() for project in self.projects],
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
            projects=[
                ResumeProjectItemSchema.from_domain_schema(schema=project)
                for project in schema.projects
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
    content: Annotated[ResumeContentSchema, Field(title="Resume content")]

    def to_create_schema(self, *, author_username: str) -> ResumeCreateParams:
        return ResumeCreateParams(
            title=self.title,
            content=self.content.to_domain_schema(),
            author_username=author_username,
        )

    def to_update_schema(self) -> ResumeUpdateParams:
        return ResumeUpdateParams(title=self.title, content=self.content.to_domain_schema())


class ResumeResponseSchema(CamelCaseSchema):
    id: Annotated[int, Field(title="Identifier")]
    title: Annotated[str, Field(title="Workspace title")]
    content: Annotated[ResumeContentSchema, Field(title="Resume content")]
    created_at: Annotated[str, Field(title="Created at")]
    updated_at: Annotated[str, Field(title="Updated at")]

    @classmethod
    def from_domain_schema(cls, *, schema: Resume) -> Self:
        return cls(
            id=schema.id,
            title=schema.title,
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
