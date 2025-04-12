from collections.abc import Iterable
from itertools import groupby
from typing import Self

from pydantic import Field

from api.schemas import CamelCaseSchema
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItems,
    Resource,
    Sheets,
    Subsections,
)


class CompetencyMatrixListItemsParams(CamelCaseSchema):
    sheet_name: str = Field(
        title="Лист",
        description="Наименование листа для фильтрации по нему",
    )


class ResourceSchema(CamelCaseSchema):
    id: int = Field(
        title="Идентификатор",
        description="Идентификатор ресурса для дополнительного изучения.",
        examples=[1, 2, 3],
    )
    name: str = Field(
        title="Наименование",
        description="Наименование ресурса для дополнительного изучения.",
        examples=["Официальная документация Python", "Блог здравого смысла"],
    )
    url: str = Field(
        title="Ссылка",
        description="Ссылка на ресурс для дополнительного изучения.",
        examples=["https://python.org/", "https://pythonz.net/"],
    )
    context: str = Field(
        title="Контекст",
        description="Контекст. Пояснение, почему был добавлен данный ресурс.",
        examples=[
            "Официальная документация - хорошее место для изучения.",
            "Блог с хорошими статьями, где можно изучить тему X.",
        ],
    )

    @classmethod
    def from_domain_schema(cls, *, schema: Resource) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
            url=schema.url,
            context=schema.context,
        )


class CompetencyMatrixItemSchema(CamelCaseSchema):
    id: int = Field(
        title="Идентификатор",
        description="Идентификатор вопроса в матрице компетенций",
        examples=[1, 2, 3],
    )
    question: str = Field(
        title="Вопрос",
        description="Вопрос в матрице компетенций",
        examples=[
            "что такое и зачем нужен Pep8?",
            "Что такое Mixin? Какие плюсы и минусы есть у такого подхода к наследованию?",
            "range - это итератор?",
        ],
    )

    @classmethod
    def from_domain_schema(cls, *, schema: CompetencyMatrixItem) -> Self:
        return cls(id=schema.id, question=schema.question)


class CompetencyMatrixItemDetailSchema(CompetencyMatrixItemSchema):
    answer: str = Field(
        title="Ответ",
        description="Ответ на вопрос",
        examples=[
            "Pep8 - это стандарт написания кода на Python",
            "Mixin - это механизм множественного наследования, позволяющий...",
            "range - это не итератор, но lazy iterable",
        ],
    )
    interview_expected_answer: str = Field(
        title="Ожидаемый ответ",
        description="Ответ, который ожидает услышать интервьюер. Содержит также пояснения.",
        examples=[
            "... Интервьюер ожидает услышать также, пишете ли вы код по Pep8 или нет.",
            "... По хорошему, нужно сказать, что вы стараетесь не использовать миксины.",
            "... Интервьюер хочет понять, насколько глубоко вы понимаете встроенные типы данных.",
        ],
    )
    sheet: str = Field(
        title="Лист",
        description="Наименование листа, на котором располагается вопрос",
        examples=["Python", "SQL"],
    )
    grade: str = Field(
        title="Компетенция",
        description="Категория компетенции вопроса (Для какого грейда этот вопрос)",
        examples=["Junior", "Middle"],
    )
    section: str = Field(
        title="Раздел",
        description="Наименование раздела вопроса",
        examples=["ООП", "Asyncio"],
    )
    subsection: str = Field(
        title="Подраздел",
        description="Наименование подраздела вопроса",
        examples=["Магические методы", "Концепция асинхронности"],
    )
    resources: list[ResourceSchema] = Field(
        title="Ресурсы",
        description="Список ресурсов для дополнительного изучения",
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
            resources=[
                ResourceSchema.from_domain_schema(schema=resource) for resource in schema.resources
            ],
        )


class CompetencyMatrixGroupedGradesSchema(CamelCaseSchema):
    grade: str = Field(
        title="Компетенция",
        description="Категория компетенции вопроса (Для какого грейда этот вопрос)",
        examples=["Junior", "Middle"],
    )
    items: list[CompetencyMatrixItemSchema] = Field(
        title="Список",
        description="Список вопросов в матрице компетенций",
    )

    @classmethod
    def from_domain_schema(cls, *, grade: str, items: Iterable[CompetencyMatrixItem]) -> Self:
        return cls(
            grade=grade,
            items=[CompetencyMatrixItemSchema.from_domain_schema(schema=item) for item in items],
        )


class CompetencyMatrixGroupedSubsectionsSchema(CamelCaseSchema):
    subsection: str = Field(
        title="Подраздел",
        description="Наименование подраздела вопроса",
        examples=["Магические методы", "Концепция асинхронности"],
    )
    grades: list[CompetencyMatrixGroupedGradesSchema] = Field(
        title="Список",
        description="Список грейдов матрицы со списками вопросов в каждом",
    )

    @classmethod
    def from_domain_schema(cls, *, subsection: str, items: Iterable[CompetencyMatrixItem]) -> Self:
        return cls(
            subsection=subsection,
            grades=[
                CompetencyMatrixGroupedGradesSchema.from_domain_schema(
                    grade=grade,
                    items=list(grade_items),
                )
                for grade, grade_items in groupby(items, key=lambda item: item.grade)
            ],
        )


class CompetencyMatrixGroupedSectionsSchema(CamelCaseSchema):
    section: str = Field(
        title="Раздел",
        description="Наименование раздела вопроса",
        examples=["ООП", "Asyncio"],
    )
    subsections: list[CompetencyMatrixGroupedSubsectionsSchema] = Field(
        title="Список",
        description="Список подразделов матрицы со списками грейдов в каждом",
    )

    @classmethod
    def from_domain_schema(cls, *, section: str, items: Iterable[CompetencyMatrixItem]) -> Self:
        return cls(
            section=section,
            subsections=[
                CompetencyMatrixGroupedSubsectionsSchema.from_domain_schema(
                    subsection=subsection,
                    items=list(items),
                )
                for subsection, subsection_items in groupby(items, key=lambda item: item.subsection)
            ],
        )


class CompetencyMatrixItemsListSchema(CamelCaseSchema):
    sheet: str = Field(
        title="Лист",
        description="Наименование листа, на котором располагается вопрос",
        examples=["Python", "SQL"],
    )
    sections: list[CompetencyMatrixGroupedSectionsSchema] = Field(
        title="Список",
        description="Список разделов матрицы со списками подразделов в каждом",
    )

    @classmethod
    def empty(cls, sheet: str) -> Self:
        return cls(sheet=sheet, sections=[])

    @classmethod
    def from_domain_schema(cls, *, sheet: str, schema: CompetencyMatrixItems) -> Self:
        for sheet_name, sheet_items in groupby(schema.values, key=lambda item: item.sheet):
            if sheet_name != sheet:
                continue
            sections = [
                CompetencyMatrixGroupedSectionsSchema.from_domain_schema(
                    section=section,
                    items=list(section_items),
                )
                for section, section_items in groupby(sheet_items, key=lambda item: item.section)
            ]
            return cls(sheet=sheet, sections=sections)
        return cls.empty(sheet=sheet)


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
