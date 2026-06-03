from typing import Self

from sqlalchemy import Enum, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_dev_utils.mixins.ids import IntegerIDMixin

from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.schemas import (
    AttachedExternalResource,
    AttachedExternalResources,
    CompetencyMatrixItem,
    ExternalResource,
)
from core.enums import PublishStatusEnum
from core.types import IntId
from infra.postgresql.models.base import BaseModel
from infra.postgresql.models.mixins.publish import PublishMixin


class ExternalResourceModel(IntegerIDMixin, BaseModel):
    name_ru: Mapped[str] = mapped_column(
        String(length=255),
        doc="Russian resource name",
    )
    name_en: Mapped[str] = mapped_column(
        String(length=255),
        doc="English resource name",
    )
    url: Mapped[str] = mapped_column(
        String(length=2048),
        doc="Resource URL",
    )

    __table_args__ = (
        Index(
            "cm_external_resource_name_ru_trgm_idx",
            func.lower(name_ru).label("name_ru_lower"),
            postgresql_using="gin",
            postgresql_ops={"name_ru_lower": "gin_trgm_ops"},
        ),
        Index(
            "cm_external_resource_name_en_trgm_idx",
            func.lower(name_en).label("name_en_lower"),
            postgresql_using="gin",
            postgresql_ops={"name_en_lower": "gin_trgm_ops"},
        ),
        Index(
            "cm_external_resource_url_trgm_idx",
            func.lower(url).label("url_lower"),
            postgresql_using="gin",
            postgresql_ops={"url_lower": "gin_trgm_ops"},
        ),
    )

    def __str__(self) -> str:
        return f'External resource "{self.name_en}"'

    @classmethod
    def from_domain_schema(cls, schema: ExternalResource) -> Self:
        return cls(
            id=schema.id,
            name_ru=schema.name_ru,
            name_en=schema.name_en,
            url=schema.url,
        )

    def to_domain_schema(self) -> ExternalResource:
        return ExternalResource(
            id=IntId(self.id),
            name_ru=self.name_ru,
            name_en=self.name_en,
            url=self.url,
        )


class CompetencyMatrixItemModel(PublishMixin, IntegerIDMixin, BaseModel):
    slug: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        index=True,
        doc="URL slug for the competency matrix question",
    )
    question_ru: Mapped[str] = mapped_column(
        String(length=255),
        doc="Russian question",
    )
    question_en: Mapped[str] = mapped_column(
        String(length=255),
        doc="English question",
    )
    answer_ru: Mapped[str] = mapped_column(
        String(),
        doc="Russian answer",
    )
    answer_en: Mapped[str] = mapped_column(
        String(),
        doc="English answer",
    )
    interview_expected_answer_ru: Mapped[str] = mapped_column(
        String(),
        doc="Russian interview expected answer",
    )
    interview_expected_answer_en: Mapped[str] = mapped_column(
        String(),
        doc="English interview expected answer",
    )
    sheet_key: Mapped[str] = mapped_column(
        String(length=255),
        doc="Stable sheet key",
    )
    sheet_ru: Mapped[str] = mapped_column(
        String(length=255),
        doc="Russian sheet name",
    )
    sheet_en: Mapped[str] = mapped_column(
        String(length=255),
        doc="English sheet name",
    )
    section_ru: Mapped[str] = mapped_column(
        String(length=255),
        doc="Russian section",
    )
    section_en: Mapped[str] = mapped_column(
        String(length=255),
        doc="English section",
    )
    subsection_ru: Mapped[str] = mapped_column(
        String(length=255),
        doc="Russian subsection",
    )
    subsection_en: Mapped[str] = mapped_column(
        String(length=255),
        doc="English subsection",
    )
    grade: Mapped[GradeEnum] = mapped_column(
        Enum(GradeEnum, native_enum=False, length=11, name="grade_enum"),
        doc="Competency grade",
    )

    resource_links: Mapped[list[ResourceToItemSecondaryModel]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
        doc="External resource links",
    )

    __table_args__ = (Index("cmi_sheet_key_idx", func.lower(sheet_key)),)

    def __str__(self) -> str:
        return f"[{self.section_en} - {self.subsection_en}] {self.question_en}"

    @classmethod
    def from_domain_schema(
        cls,
        item: CompetencyMatrixItem,
        *,
        include_relationships: bool,
    ) -> Self:
        return cls(
            pk=item.id,
            slug=item.slug,
            question_ru=item.question_ru,
            question_en=item.question_en,
            answer_ru=item.answer_ru,
            answer_en=item.answer_en,
            publish_status=item.publish_status,
            interview_expected_answer_ru=item.interview_expected_answer_ru,
            interview_expected_answer_en=item.interview_expected_answer_en,
            sheet_key=item.sheet_key,
            sheet_ru=item.sheet_ru,
            sheet_en=item.sheet_en,
            section_ru=item.section_ru,
            section_en=item.section_en,
            subsection_ru=item.subsection_ru,
            subsection_en=item.subsection_en,
            grade=item.grade,
            resource_links=[
                ResourceToItemSecondaryModel.from_domain_schema(schema=resource)
                for resource in item.resources
            ]
            if include_relationships
            else [],
        )

    def update_from_domain_schema(self, item: CompetencyMatrixItem) -> None:
        self.slug = item.slug
        self.question_ru = item.question_ru
        self.question_en = item.question_en
        self.answer_ru = item.answer_ru
        self.answer_en = item.answer_en
        self.publish_status = item.publish_status
        self.interview_expected_answer_ru = item.interview_expected_answer_ru
        self.interview_expected_answer_en = item.interview_expected_answer_en
        self.sheet_key = item.sheet_key
        self.sheet_ru = item.sheet_ru
        self.sheet_en = item.sheet_en
        self.section_ru = item.section_ru
        self.section_en = item.section_en
        self.subsection_ru = item.subsection_ru
        self.subsection_en = item.subsection_en
        if item.grade is not None:
            self.grade = item.grade

    def to_domain_schema(self, *, include_relationships: bool) -> CompetencyMatrixItem:
        return CompetencyMatrixItem(
            id=IntId(self.pk),
            slug=self.slug,
            question_ru=self.question_ru,
            question_en=self.question_en,
            answer_ru=self.answer_ru,
            answer_en=self.answer_en,
            publish_status=PublishStatusEnum.from_value(self.publish_status),
            interview_expected_answer_ru=self.interview_expected_answer_ru,
            interview_expected_answer_en=self.interview_expected_answer_en,
            sheet_key=self.sheet_key,
            sheet_ru=self.sheet_ru,
            sheet_en=self.sheet_en,
            section_ru=self.section_ru,
            section_en=self.section_en,
            subsection_ru=self.subsection_ru,
            subsection_en=self.subsection_en,
            grade=self.grade,
            resources=AttachedExternalResources(
                values=(
                    [link.to_domain_schema() for link in self.resource_links]
                    if include_relationships
                    else []
                ),
            ),
        )


class ResourceToItemSecondaryModel(IntegerIDMixin, BaseModel):
    item_id: Mapped[int] = mapped_column(
        ForeignKey(CompetencyMatrixItemModel.id, ondelete="CASCADE"),
        doc="Competency matrix item identifier",
    )
    resource_id: Mapped[int] = mapped_column(
        ForeignKey(ExternalResourceModel.id, ondelete="CASCADE"),
        doc="External resource identifier",
    )
    context_ru: Mapped[str] = mapped_column(
        String(),
        doc="Russian context for why the resource was attached",
    )
    context_en: Mapped[str] = mapped_column(
        String(),
        doc="English context for why the resource was attached",
    )

    item: Mapped[CompetencyMatrixItemModel] = relationship(
        back_populates="resource_links",
        doc="Competency matrix item",
    )
    resource: Mapped[ExternalResourceModel] = relationship(
        doc="External resource",
    )

    __table_args__ = (UniqueConstraint("item_id", "resource_id", name="cm_resource_item_uniq"),)

    @classmethod
    def from_domain_schema(cls, schema: AttachedExternalResource) -> Self:
        return cls(
            resource_id=schema.id,
            resource=ExternalResourceModel.from_domain_schema(
                schema=schema.to_external_resource(),
            ),
            context_ru=schema.context_ru,
            context_en=schema.context_en,
        )

    def to_domain_schema(self) -> AttachedExternalResource:
        return AttachedExternalResource(
            id=IntId(self.resource.id),
            name_ru=self.resource.name_ru,
            name_en=self.resource.name_en,
            url=self.resource.url,
            context_ru=self.context_ru,
            context_en=self.context_en,
        )
