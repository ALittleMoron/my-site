import datetime
from typing import Self

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Identity,
    Index,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.competency_matrix.enums import StatusEnum
from app.core.competency_matrix.schemas import (
    FullCompetencyMatrixItem,
    Grade,
    Resource,
    Section,
    Sheet,
    ShortCompetencyMatrixItem,
    Subsection,
)
from app.database.models.base import Base

DjangoIdIdentity = Identity(
    start=1,
    increment=1,
    minvalue=1,
    maxvalue=9223372036854775807,
    cycle=False,
    cache=1,
)


items_to_resources = Table(
    'competency_matrix_item_resources',
    Base.metadata,
    Column('id', BigInteger, DjangoIdIdentity, primary_key=True),
    Column('competencymatrixitem_id', BigInteger, nullable=False),
    Column('resource_id', BigInteger, nullable=False),
    ForeignKeyConstraint(
        ['competencymatrixitem_id'],
        ['competency_matrix_item.id'],
        deferrable=True,
        initially='DEFERRED',
        name='competency_matrix_it_competencymatrixitem_49738da7_fk_competenc',
    ),
    ForeignKeyConstraint(
        ['resource_id'],
        ['competency_matrix_resource.id'],
        deferrable=True,
        initially='DEFERRED',
        name='competency_matrix_it_resource_id_9cca1b04_fk_competenc',
    ),
)


class SheetModel(Base):
    __tablename__ = 'competency_matrix_sheet'

    id: Mapped[int] = mapped_column(BigInteger, DjangoIdIdentity, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    @classmethod
    def from_schema(cls, schema: Sheet) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
        )

    def to_schema(self) -> Sheet:
        return Sheet(id=self.id, name=self.name)


class GradeModel(Base):
    __tablename__ = 'competency_matrix_grade'

    id: Mapped[int] = mapped_column(BigInteger, DjangoIdIdentity, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    @classmethod
    def from_schema(cls, schema: Grade) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
        )


class SectionModel(Base):
    __tablename__ = 'competency_matrix_section'

    id: Mapped[int] = mapped_column(BigInteger, DjangoIdIdentity, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    sheet_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            'competency_matrix_sheet.id',
            deferrable=True,
            initially='DEFERRED',
            name='competency_matrix_se_sheet_id_2a900665_fk_competenc',
        ),
    )

    sheet: Mapped['SheetModel'] = relationship()

    @classmethod
    def from_schema(cls, schema: Section) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
            sheet=SheetModel.from_schema(schema=schema.sheet),
        )


class SubsectionModel(Base):
    __tablename__ = 'competency_matrix_subsection'
    __table_args__ = (
        Index(
            'competency_matrix_subsection_section_id_04530e5d',
            'section_id',
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, DjangoIdIdentity, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    section_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            'competency_matrix_section.id',
            deferrable=True,
            initially='DEFERRED',
            name='competency_matrix_su_section_id_04530e5d_fk_competenc',
        ),
    )

    section: Mapped['SectionModel'] = relationship()

    @classmethod
    def from_schema(cls, schema: Subsection) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
            section=SectionModel.from_schema(schema=schema.section),
        )


class ResourceModel(Base):
    __tablename__ = 'competency_matrix_resource'

    id: Mapped[int] = mapped_column(BigInteger, DjangoIdIdentity, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(200))
    context: Mapped[str] = mapped_column(Text)

    @classmethod
    def from_schema(cls, schema: Resource) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
            url=schema.url,
            context=schema.context,
        )


class CompetencyMatrixItemModel(Base):
    __tablename__ = 'competency_matrix_item'
    __table_args__ = (
        Index('competency_matrix_item_grade_id_8e9263cf', 'grade_id'),
        Index('competency_matrix_item_subsection_id_5e0d9444', 'subsection_id'),
    )

    id: Mapped[int] = mapped_column(BigInteger, DjangoIdIdentity, primary_key=True)
    status: Mapped[str] = mapped_column(String(100))
    status_changed: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    question: Mapped[str] = mapped_column(String(255))
    answer: Mapped[str] = mapped_column(Text)
    interview_expected_answer: Mapped[str] = mapped_column(Text)
    grade_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "competency_matrix_grade.id",
            deferrable=True,
            initially='DEFERRED',
            name='competency_matrix_it_grade_id_8e9263cf_fk_competenc',
        ),
    )
    subsection_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "competency_matrix_subsection.id",
            deferrable=True,
            initially='DEFERRED',
            name='competency_matrix_it_subsection_id_5e0d9444_fk_competenc',
        ),
    )

    grade: Mapped['GradeModel | None'] = relationship()
    subsection: Mapped['SubsectionModel | None'] = relationship()
    resources: Mapped[list['ResourceModel']] = relationship(secondary=items_to_resources)

    @classmethod
    def from_domain_schema(cls, schema: FullCompetencyMatrixItem) -> Self:
        return cls(
            id=schema.id,
            status=schema.status,
            status_changed=schema.status_changed,
            question=schema.question,
            answer=schema.answer,
            interview_expected_answer=schema.interview_expected_answer,
            grade_id=schema.grade_id,
            subsection_id=schema.subsection_id,
            grade=GradeModel.from_schema(schema=schema.grade) if schema.grade is not None else None,
            subsection=(
                SubsectionModel.from_schema(schema=schema.subsection)
                if schema.subsection is not None
                else None
            ),
            resources=[ResourceModel.from_schema(schema=resource) for resource in schema.resources],
        )

    def to_short_domain_schema(self) -> "ShortCompetencyMatrixItem":
        return ShortCompetencyMatrixItem(
            id=self.id,
            question=self.question,
            status=StatusEnum(self.status),
            status_changed=self.status_changed,
            grade_id=self.grade_id,
            subsection_id=self.subsection_id,
        )
