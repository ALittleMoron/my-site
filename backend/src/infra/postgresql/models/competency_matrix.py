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
    name: Mapped[str] = mapped_column(
        String(length=255),
        doc="Название ресурса",
    )
    url: Mapped[str] = mapped_column(
        String(length=2048),
        doc="Ссылка на ресурс.",
    )

    __table_args__ = (
        Index(
            "cm_external_resource_name_trgm_idx",
            func.lower(name).label("name_lower"),
            postgresql_using="gin",
            postgresql_ops={"name_lower": "gin_trgm_ops"},
        ),
        Index(
            "cm_external_resource_url_trgm_idx",
            func.lower(url).label("url_lower"),
            postgresql_using="gin",
            postgresql_ops={"url_lower": "gin_trgm_ops"},
        ),
    )

    def __str__(self) -> str:
        return f'Внешний ресурс "{self.name}"'

    @classmethod
    def from_domain_schema(cls, schema: ExternalResource) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
            url=schema.url,
        )

    def to_domain_schema(self) -> ExternalResource:
        return ExternalResource(
            id=IntId(self.id),
            name=self.name,
            url=self.url,
        )


class CompetencyMatrixItemModel(PublishMixin, IntegerIDMixin, BaseModel):
    question: Mapped[str] = mapped_column(
        String(length=255),
        doc="Вопрос",
    )
    answer: Mapped[str] = mapped_column(
        String(),
        doc="Ответ на вопрос",
    )
    interview_expected_answer: Mapped[str] = mapped_column(
        String(),
        doc="Ответ, который ожидают на интервью",
    )
    sheet: Mapped[str] = mapped_column(
        String(length=255),
        doc="Лист",
    )
    section: Mapped[str] = mapped_column(
        String(length=255),
        doc="Раздел",
    )
    subsection: Mapped[str] = mapped_column(
        String(length=255),
        doc="Подраздел",
    )
    grade: Mapped[GradeEnum] = mapped_column(
        Enum(GradeEnum, native_enum=False, length=11, name="grade_enum"),
        doc="Уровень компетенции",
    )

    resource_links: Mapped[list[ResourceToItemSecondaryModel]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
        doc="Связи с внешними ресурсами",
    )

    __table_args__ = (Index("cmi_sheet_idx", func.lower("sheet")),)

    def __str__(self) -> str:
        return f"[{self.section} - {self.subsection}] {self.question}"

    @classmethod
    def from_domain_schema(
        cls,
        item: CompetencyMatrixItem,
        *,
        include_relationships: bool,
    ) -> Self:
        return cls(
            pk=item.id,
            question=item.question,
            answer=item.answer,
            publish_status=item.publish_status,
            interview_expected_answer=item.interview_expected_answer,
            sheet=item.sheet,
            section=item.section,
            subsection=item.subsection,
            grade=item.grade,
            resource_links=[
                ResourceToItemSecondaryModel.from_domain_schema(schema=resource)
                for resource in item.resources
            ]
            if include_relationships
            else [],
        )

    def update_from_domain_schema(self, item: CompetencyMatrixItem) -> None:
        self.question = item.question
        self.answer = item.answer
        self.publish_status = item.publish_status
        self.interview_expected_answer = item.interview_expected_answer
        self.sheet = item.sheet
        self.section = item.section
        self.subsection = item.subsection
        if item.grade is not None:
            self.grade = item.grade

    def to_domain_schema(self, *, include_relationships: bool) -> CompetencyMatrixItem:
        return CompetencyMatrixItem(
            id=IntId(self.pk),
            question=self.question,
            answer=self.answer,
            publish_status=PublishStatusEnum.from_value(self.publish_status),
            interview_expected_answer=self.interview_expected_answer,
            sheet=self.sheet,
            section=self.section,
            subsection=self.subsection,
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
        doc="Идентификатор элемента матрицы компетенций",
    )
    resource_id: Mapped[int] = mapped_column(
        ForeignKey(ExternalResourceModel.id, ondelete="CASCADE"),
        doc="Идентификатор внешнего ресурса",
    )
    context: Mapped[str] = mapped_column(
        String(),
        doc="Контекст того, почему ресурс был прикреплен к вопросу.",
    )

    item: Mapped[CompetencyMatrixItemModel] = relationship(
        back_populates="resource_links",
        doc="Элемент матрицы компетенций",
    )
    resource: Mapped[ExternalResourceModel] = relationship(
        doc="Внешний ресурс",
    )

    __table_args__ = (UniqueConstraint("item_id", "resource_id", name="cm_resource_item_uniq"),)

    @classmethod
    def from_domain_schema(cls, schema: AttachedExternalResource) -> Self:
        return cls(
            resource_id=schema.id,
            resource=ExternalResourceModel.from_domain_schema(
                schema=schema.to_external_resource(),
            ),
            context=schema.context,
        )

    def to_domain_schema(self) -> AttachedExternalResource:
        return AttachedExternalResource(
            id=IntId(self.resource.id),
            name=self.resource.name,
            url=self.resource.url,
            context=self.context,
        )
