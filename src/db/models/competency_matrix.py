from typing import Self

from sqlalchemy import ForeignKey, Index, String, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_dev_utils.mixins.ids import IntegerIDMixin

from core.competency_matrix.enums import StatusEnum, GradeEnum
from core.competency_matrix.schemas import CompetencyMatrixItem, ExternalResource, ExternalResources
from db.models.abc import PublishModel
from db.models.base import Base


class ResourceToItemSecondaryModel(Base, IntegerIDMixin):
    """Связь M2M внешнего ресурса к элементу матрицы компетенций."""

    item_id: Mapped[int] = mapped_column(
        ForeignKey("competency_matrix_items.id", ondelete="CASCADE"),
        doc="Идентификатор элемента матрицы компетенций",
    )
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("competency_matrix_resources.id", ondelete="CASCADE"),
        doc="Идентификатор внешнего ресурса",
    )

    __tablename__ = "resource_to_item_secondary"


class ExternalResourceModel(Base, IntegerIDMixin):
    """Внешний ресурс"""

    name: Mapped[str] = mapped_column(
        String(length=255),
        doc="Название ресурса",
    )
    url: Mapped[str] = mapped_column(
        String(length=2048),
        doc="Ссылка на ресурс.",
    )
    context: Mapped[str] = mapped_column(
        String(),
        doc="Контекст того, почему ресурс вообще был прикреплен к вопросу.",
    )

    __tablename__ = "competency_matrix_resources"

    def __str__(self) -> str:
        return f'Внешний ресурс "{self.name}"'

    @classmethod
    def from_domain_schema(cls, schema: ExternalResource) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
            url=schema.url,
            context=schema.context,
        )

    def to_domain_schema(self) -> ExternalResource:
        return ExternalResource(
            id=self.id,
            name=self.name,
            url=self.url,
            context=self.context,
        )


class CompetencyMatrixItemModel(PublishModel, IntegerIDMixin):
    """Элемент матрицы компетенций"""

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
        Enum(GradeEnum, native_enum=False, length=11),
        doc="Уровень компетенции",
    )

    resources: Mapped[list[ExternalResourceModel]] = relationship(
        doc="Внешние ресурсы",
        secondary="resource_to_item_secondary",
    )

    __tablename__ = "competency_matrix_items"
    __table_args__ = (
        Index(
            "cmi_sheet_idx",
            func.lower("sheet"),
        ),
    )

    def __str__(self) -> str:
        return f"[{self.section} - {self.subsection}] {self.question}"

    @classmethod
    def from_domain_schema(cls, item: CompetencyMatrixItem) -> Self:
        return cls(
            pk=item.id,
            question=item.question,
            answer=item.answer,
            status=item.status,
            interview_expected_answer=item.interview_expected_answer,
            sheet=item.sheet,
            section=item.section,
            subsection=item.subsection,
            grade=item.grade,
            resources=[
                ExternalResourceModel.from_domain_schema(schema=resource)
                for resource in item.resources
            ],
        )

    def to_domain_schema(self, *, include_relationships: bool) -> CompetencyMatrixItem:
        return CompetencyMatrixItem(
            id=self.pk,
            question=self.question,
            answer=self.answer,
            status=StatusEnum(self.status),
            interview_expected_answer=self.interview_expected_answer,
            sheet=self.sheet,
            section=self.section,
            subsection=self.subsection,
            grade=self.grade,
            resources=ExternalResources(
                values=(
                    [resource.to_domain_schema() for resource in self.resources]
                    if include_relationships
                    else []
                ),
            ),
        )
