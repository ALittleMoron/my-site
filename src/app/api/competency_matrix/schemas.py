from typing import Self

from pydantic import Field

from app.api.schemas import CamelCaseSchema
from app.core.competency_matrix.schemas import (
    FilledCompetencyMatrixItems,
    ShortFilledCompetencyMatrixItem,
)


class CompetencyMatrixBaseSchema(CamelCaseSchema):
    id: int = Field(
        ...,
        title="Идентификатор",
        description="Идентификатор вопроса в матрице компетенций",
        examples=[1, 2, 3],
    )
    question: str = Field(
        ...,
        title="Вопрос",
        description="Вопрос в матрице компетенций",
        examples=[
            "что такое и зачем нужен Pep8?",
            "Что такое Mixin? Какие плюсы и минусы есть у такого подхода к наследованию?",
            "range - это итератор?",
        ],
    )
    grade_id: int = Field(
        ...,
        title="Идентификатор",
        description="Идентификатор компетенции",
        examples=[1, 2, 3],
    )
    subsection_id: int = Field(
        ...,
        title="Идентификатор",
        description="Идентификатор подраздела",
        examples=[1, 2, 3],
    )

    @classmethod
    def from_domain_schema(cls, *, schema: ShortFilledCompetencyMatrixItem) -> Self:
        return cls(
            id=schema.id,
            question=schema.question,
            grade_id=schema.grade_id,
            subsection_id=schema.subsection_id,
        )


class CompetencyMatrixListSchema(CamelCaseSchema):
    items: list[CompetencyMatrixBaseSchema] = Field(
        ...,
        title="Список",
        description="Список вопросов в матрице компетенций",
    )

    @classmethod
    def from_domain_schema(cls, *, schema: FilledCompetencyMatrixItems) -> Self:
        return cls(
            items=[
                CompetencyMatrixBaseSchema.from_domain_schema(schema=item) for item in schema.values
            ],
        )
