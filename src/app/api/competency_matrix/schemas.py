from typing import Self

from pydantic import Field

from app.api.schemas import CamelCaseSchema
from app.core.competency_matrix.schemas import (
    FilledCompetencyMatrixItems,
    FullFilledCompetencyMatrixItem,
    Grade,
    ListItemsParams,
    ListSubsectionsParams,
    Resource,
    Resources,
    Section,
    Sheet,
    Sheets,
    ShortFilledCompetencyMatrixItem,
    Subsection,
    Subsections,
)


class CompetencyMatrixListItemsParams(CamelCaseSchema):
    sheet_id: int

    def to_schema(self) -> ListItemsParams:
        return ListItemsParams(sheet_id=self.sheet_id)


class CompetencyMatrixListSubsectionsParams(CamelCaseSchema):
    sheet_id: int

    def to_schema(self) -> ListSubsectionsParams:
        return ListSubsectionsParams(sheet_id=self.sheet_id)


class CompetencyMatrixItemBaseSchema(CamelCaseSchema):
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


class CompetencyMatrixItemsListSchema(CamelCaseSchema):
    items: list[CompetencyMatrixItemBaseSchema] = Field(
        ...,
        title="Список",
        description="Список вопросов в матрице компетенций",
    )

    @classmethod
    def from_domain_schema(cls, *, schema: FilledCompetencyMatrixItems) -> Self:
        return cls(
            items=[
                CompetencyMatrixItemBaseSchema.from_domain_schema(schema=item)
                for item in schema.values
            ],
        )


class CompetencyMatrixSheetsBaseSchema(CamelCaseSchema):
    id: int = Field(
        ...,
        title="Идентификатор",
        description="Идентификатор листа с вопросами в матрице компетенций",
        examples=[1, 2, 3],
    )
    name: str = Field(
        ...,
        title="Наименование",
        description="Наименование листа с вопросами в матрице компетенций",
        examples=["Python", "JavaScript", "PHP"],
    )

    @classmethod
    def from_domain_schema(cls, *, schema: Sheet) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
        )


class CompetencyMatrixSheetsListSchema(CamelCaseSchema):
    sheets: list[CompetencyMatrixSheetsBaseSchema] = Field(
        ...,
        title="Список",
        description="Список листов матрицы компетенций",
    )

    @classmethod
    def from_domain_schema(cls, *, schema: Sheets) -> Self:
        return cls(
            sheets=[
                CompetencyMatrixSheetsBaseSchema.from_domain_schema(schema=item)
                for item in schema.values
            ],
        )


class CompetencyMatrixSectionBaseSchema(CamelCaseSchema):
    id: int = Field(
        ...,
        title="Идентификатор",
        description="Идентификатор раздела в матрице компетенций",
        examples=[1, 2, 3],
    )
    name: str = Field(
        ...,
        title="Наименование",
        description="Наименование раздела в матрице компетенций",
        examples=["Основы", "ООП", "Асинхронное программирование"],
    )

    @classmethod
    def from_domain_schema(cls, *, schema: Section) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
        )


class CompetencyMatrixSectionSchema(CompetencyMatrixSectionBaseSchema):
    sheet: CompetencyMatrixSectionBaseSchema = Field(
        ...,
        title="Лист",
        description="Лист с вопросами в матрице компетенций",
    )

    @classmethod
    def from_domain_schema(cls, *, schema: Section) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
            sheet=CompetencyMatrixSheetsBaseSchema.from_domain_schema(schema=schema.sheet),
        )


class CompetencyMatrixSubsectionBaseSchema(CamelCaseSchema):
    id: int = Field(
        ...,
        title="Идентификатор",
        description="Идентификатор подраздела в матрице компетенций",
        examples=[1, 2, 3],
    )
    name: str = Field(
        ...,
        title="Наименование",
        description="Наименование подраздела в матрице компетенций",
        examples=["Функции", "Магические методы", "Лексические структуры"],
    )

    @classmethod
    def from_domain_schema(cls, *, schema: Subsection) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
        )


class CompetencyMatrixSubsectionSchema(CompetencyMatrixSubsectionBaseSchema):
    section: CompetencyMatrixSectionSchema = Field(
        ...,
        title="Раздел",
        description="Раздел, в котором находится подраздел",
    )

    @classmethod
    def from_domain_schema(cls, *, schema: Subsection) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
            section=CompetencyMatrixSectionSchema.from_domain_schema(schema=schema.section),
        )


class CompetencyMatrixSubsectionsListSchema(CamelCaseSchema):
    subsections: list[CompetencyMatrixSubsectionSchema] = Field(
        ...,
        title="Список",
        description="Список подразделов матрицы компетенций",
    )

    @classmethod
    def from_domain_schema(cls, *, schema: Subsections) -> Self:
        return cls(
            subsections=[
                CompetencyMatrixSubsectionSchema.from_domain_schema(schema=item)
                for item in schema.values
            ],
        )


class CompetencyMatrixGradeSchema(CamelCaseSchema):
    id: int = Field(
        ...,
        title="Идентификатор",
        description="Идентификатор компетенции",
        examples=[1, 2, 3],
    )
    name: str = Field(
        ...,
        title="Наименование",
        description="Наименование компетенции",
        examples=["Junior", "Middle", "Junior+", "Middle+"],
    )

    @classmethod
    def from_domain_schema(cls, *, schema: Grade) -> Self:
        return cls(
            id=schema.id,
            name=schema.name,
        )


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
    grade: CompetencyMatrixGradeSchema = Field(
        ...,
        title="Компетенция",
        description="Категория компетенции вопроса (Для какого грейда этот вопрос)",
    )
    subsection: CompetencyMatrixSubsectionSchema = Field(
        ...,
        title="Подраздел",
        description="Подраздел вопроса",
    )
    resources: list[CompetencyMatrixResourceSchema] = Field(
        ...,
        title="Подраздел",
        description="Подраздел вопроса",
    )

    @classmethod
    def from_domain_schema(cls, *, schema: FullFilledCompetencyMatrixItem) -> Self:
        return cls(
            id=schema.id,
            question=schema.question,
            answer=schema.answer,
            interview_expected_answer=schema.interview_expected_answer,
            grade=CompetencyMatrixGradeSchema.from_domain_schema(schema=schema.grade),
            subsection=CompetencyMatrixSubsectionSchema.from_domain_schema(
                schema=schema.subsection,
            ),
            resources=CompetencyMatrixResourceSchema.from_domain_schema_list(
                schema=schema.resources,
            ),
        )
