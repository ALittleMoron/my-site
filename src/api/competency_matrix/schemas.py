from typing import Self

from pydantic import Field

from api.schemas import CamelCaseSchema
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItems,
    Resource,
    Resources,
    Sheets,
    Subsections,
)


class CompetencyMatrixListItemsParams(CamelCaseSchema):
    sheet_name: str = Field(
        ...,
        title="Лист",
        description="Наименование листа для фильтрации по нему",
    )


class CompetencyMatrixItemSchema(CamelCaseSchema):
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
    sheet: str = Field(
        ...,
        title="Лист",
        description="Наименование листа, на котором располагается вопрос",
        examples=["Python", "SQL"],
    )
    grade: str = Field(
        ...,
        title="Компетенция",
        description="Категория компетенции вопроса (Для какого грейда этот вопрос)",
        examples=["Junior", "Middle"],
    )
    section: str = Field(
        ...,
        title="Раздел",
        description="Наименование раздела вопроса",
        examples=["ООП", "Asyncio"],
    )
    subsection: str = Field(
        ...,
        title="Подраздел",
        description="Наименование подраздела вопроса",
        examples=["Магические методы", "Концепция асинхронности"],
    )

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixItem) -> Self:
        return cls(
            id=schema.id,
            question=schema.question,
            sheet=schema.sheet,
            grade=schema.grade,
            section=schema.section,
            subsection=schema.subsection,
        )


class CompetencyMatrixItemsListSchema(CamelCaseSchema):
    items: list[CompetencyMatrixItemSchema] = Field(
        ...,
        title="Список",
        description="Список вопросов в матрице компетенций",
    )

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixItems) -> Self:
        return cls(
            items=[
                CompetencyMatrixItemSchema.from_domain_schema(schema=item) for item in schema.values
            ],
        )


class CompetencyMatrixSubsectionsListSchema(CamelCaseSchema):
    subsections: list[str] = Field(
        ...,
        title="Список",
        description="Список листов матрицы компетенций",
    )

    @classmethod
    def from_domain_schema(cls, *, schema: Subsections) -> Self:
        return cls(subsections=schema.values)


class CompetencyMatrixSheetsListSchema(CamelCaseSchema):
    sheets: list[str] = Field(
        ...,
        title="Список",
        description="Список листов матрицы компетенций",
    )

    @classmethod
    def from_domain_schema(cls, *, schema: Sheets) -> Self:
        return cls(sheets=schema.values)


class CompetencyMatrixResourceSchema(CamelCaseSchema):
    id: int
    name: str
    url: str
    context: str = ""

    @classmethod
    def from_domain_schema(cls, *, schema: Resource) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
            url=schema.url,
            context=schema.context,
        )

    @classmethod
    def from_domain_schema_list(cls, *, schema: Resources) -> list[Self]:
        return [cls.from_domain_schema(schema=resource) for resource in schema.values]


class CompetencyMatrixItemDetailSchema(CamelCaseSchema):
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
    answer: str = Field(
        ...,
        title="Ответ",
        description="Подробный ответ на вопрос",
        examples=[
            "Да",
            "Нет",
            "Что-то более длинное... Вообще, это текст со стилями, так что тут может быть всё",
        ],
    )
    interview_expected_answer: str = Field(
        ...,
        title="Ожидаемый ответ",
        description="Ответ, который хочет услышать интервьюер",
        examples=[
            "Да",
            "Нет",
            "Что-то более длинное... Вообще, это текст со стилями, так что тут может быть всё",
        ],
    )
    sheet: str = Field(
        ...,
        title="Лист",
        description="Наименование листа, на котором располагается вопрос",
        examples=["Python", "SQL"],
    )
    grade: str = Field(
        ...,
        title="Компетенция",
        description="Категория компетенции вопроса (Для какого грейда этот вопрос)",
        examples=["Junior", "Middle"],
    )
    section: str = Field(
        ...,
        title="Раздел",
        description="Наименование раздела вопроса",
        examples=["ООП", "Asyncio"],
    )
    subsection: str = Field(
        ...,
        title="Подраздел",
        description="Наименование подраздела вопроса",
        examples=["Магические методы", "Концепция асинхронности"],
    )
    resources: list[CompetencyMatrixResourceSchema] = Field(
        ...,
        title="Подраздел",
        description="Подраздел вопроса",
    )

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixItem) -> Self:
        return cls(
            id=schema.id,
            question=schema.question,
            answer=schema.answer,
            interview_expected_answer=schema.interview_expected_answer,
            sheet=schema.sheet,
            grade=schema.grade,
            section=schema.section,
            subsection=schema.subsection,
            resources=CompetencyMatrixResourceSchema.from_domain_schema_list(
                schema=schema.resources,
            ),
        )
