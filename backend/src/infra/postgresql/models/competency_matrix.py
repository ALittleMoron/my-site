from datetime import datetime
from typing import Self

from sqlalchemy import Enum, ForeignKey, Index, String, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_dev_utils.mixins.ids import IntegerIDMixin
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.schemas import (
    AttachedExternalResource,
    AttachedExternalResources,
    CompetencyMatrixItem,
    ExternalResource,
    QueuedCompetencyMatrixQuestion,
    QueuedCompetencyMatrixQuestionCreateParams,
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
    grade: Mapped[GradeEnum | None] = mapped_column(
        Enum(GradeEnum, native_enum=False, length=11, name="grade_enum"),
        doc="Competency grade",
    )

    resource_links: Mapped[list[ResourceToItemSecondaryModel]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
        doc="External resource links",
    )

    __table_args__ = (
        Index(
            "cmi_sheet_key_status_order_idx",
            func.lower(sheet_key).label("sheet_key_lower"),
            "publish_status",
            section_en,
            subsection_en,
            grade,
            "id",
        ),
        Index(
            "cmi_workspace_status_published_at_idx",
            "publish_status",
            text("published_at DESC NULLS LAST"),
            "id",
        ),
        Index(
            "cmi_workspace_sheet_status_grade_idx",
            sheet_key,
            "publish_status",
            grade,
            "id",
            postgresql_include=("sheet_key", "sheet_ru", "sheet_en"),
        ),
        Index(
            "cmi_workspace_ru_structure_idx",
            section_ru,
            subsection_ru,
            grade,
            "id",
            postgresql_include=("sheet_key", "publish_status"),
        ),
        Index(
            "cmi_workspace_en_structure_idx",
            section_en,
            subsection_en,
            grade,
            "id",
            postgresql_include=("sheet_key", "publish_status"),
        ),
        Index(
            "cmi_workspace_missing_fields_idx",
            text(
                "((length(trim(slug)) = 0) OR "
                "(length(trim(sheet_key)) = 0) OR "
                "(grade IS NULL) OR "
                "(length(trim(question_ru)) = 0) OR "
                "(length(trim(question_en)) = 0) OR "
                "(length(trim(answer_ru)) = 0) OR "
                "(length(trim(answer_en)) = 0) OR "
                "(length(trim(interview_expected_answer_ru)) = 0) OR "
                "(length(trim(interview_expected_answer_en)) = 0) OR "
                "(length(trim(sheet_ru)) = 0) OR "
                "(length(trim(sheet_en)) = 0) OR "
                "(length(trim(section_ru)) = 0) OR "
                "(length(trim(section_en)) = 0) OR "
                "(length(trim(subsection_ru)) = 0) OR "
                "(length(trim(subsection_en)) = 0))",
            ),
        ),
        Index(
            "cmi_workspace_slug_trgm_idx",
            func.lower(slug).label("workspace_slug_lower"),
            postgresql_using="gin",
            postgresql_ops={"workspace_slug_lower": "gin_trgm_ops"},
        ),
        Index(
            "cmi_workspace_question_ru_trgm_idx",
            func.lower(question_ru).label("workspace_question_ru_lower"),
            postgresql_using="gin",
            postgresql_ops={"workspace_question_ru_lower": "gin_trgm_ops"},
        ),
        Index(
            "cmi_workspace_question_en_trgm_idx",
            func.lower(question_en).label("workspace_question_en_lower"),
            postgresql_using="gin",
            postgresql_ops={"workspace_question_en_lower": "gin_trgm_ops"},
        ),
    )

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
            published_at=item.published_at,
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
        if item.published_at is not None:
            self.published_at = item.published_at
        self.interview_expected_answer_ru = item.interview_expected_answer_ru
        self.interview_expected_answer_en = item.interview_expected_answer_en
        self.sheet_key = item.sheet_key
        self.sheet_ru = item.sheet_ru
        self.sheet_en = item.sheet_en
        self.section_ru = item.section_ru
        self.section_en = item.section_en
        self.subsection_ru = item.subsection_ru
        self.subsection_en = item.subsection_en
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
            published_at=self.published_at,
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


class QueuedQuestionModel(IntegerIDMixin, BaseModel):
    question: Mapped[str] = mapped_column(
        String(length=255),
        doc="Suggested or imported raw competency matrix question",
    )
    grade: Mapped[GradeEnum | None] = mapped_column(
        Enum(GradeEnum, native_enum=False, length=11, name="grade_enum"),
        doc="Optional competency grade",
    )
    sheet: Mapped[str | None] = mapped_column(
        String(length=255),
        doc="Optional sheet name or key",
    )
    section: Mapped[str | None] = mapped_column(
        String(length=255),
        doc="Optional section",
    )
    subsection: Mapped[str | None] = mapped_column(
        String(length=255),
        doc="Optional subsection",
    )
    suggested_by_username: Mapped[str | None] = mapped_column(
        String(length=255),
        ForeignKey("auth__user_model.username", ondelete="SET NULL"),
        doc="Username that suggested the question",
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True),
        doc="Queue insertion time",
    )

    __table_args__ = (
        Index("cm_queued_question_fifo_idx", created_at),
        Index("cm_queued_question_suggested_by_idx", suggested_by_username),
    )

    @classmethod
    def from_create_params(
        cls,
        *,
        params: QueuedCompetencyMatrixQuestionCreateParams,
        created_at: datetime,
    ) -> Self:
        return cls(
            question=params.question,
            grade=None,
            sheet=None,
            section=None,
            subsection=None,
            suggested_by_username=None,
            created_at=created_at,
        )

    @classmethod
    def from_domain_schema(cls, schema: QueuedCompetencyMatrixQuestion) -> Self:
        return cls(
            id=schema.id,
            question=schema.question,
            grade=schema.grade,
            sheet=schema.sheet,
            section=schema.section,
            subsection=schema.subsection,
            suggested_by_username=schema.suggested_by_username,
            created_at=schema.created_at,
        )

    def to_domain_schema(self) -> QueuedCompetencyMatrixQuestion:
        return QueuedCompetencyMatrixQuestion(
            id=IntId(self.id),
            question=self.question,
            grade=self.grade,
            sheet=self.sheet,
            section=self.section,
            subsection=self.subsection,
            suggested_by_username=self.suggested_by_username,
            created_at=self.created_at,
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
