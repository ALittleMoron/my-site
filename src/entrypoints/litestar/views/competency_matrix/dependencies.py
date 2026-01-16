from typing import Annotated

from litestar.openapi.spec.example import Example
from litestar.params import Parameter

from entrypoints.litestar.views.competency_matrix.enums import CompetencyMatrixLayoutEnum

Layout = Annotated[
    str,
    Parameter(
        query="layout",
        default="list",
        required=False,
        description="Способ отображения элементов матрицы компетенций",
        examples=[
            Example(
                summary="Отображение списком",
                description="Отображение в виде списка блоков",
                value="list",
            ),
            Example(
                summary="Отображение сеткой",
                description="Отображение в виде сетки / таблицы",
                value="grid",
            ),
        ],
    ),
]
SheetName = Annotated[
    str,
    Parameter(
        query="sheetName",
        required=True,
        description="Название матрицы компетенций",
        examples=[
            Example(summary="Пример 1", value="Python"),
            Example(summary="Пример 2", value="SQL"),
        ],
    ),
]
OnlyPublished = Annotated[
    bool,
    Parameter(
        query="onlyPublished",
        required=False,
        description="Показывать только опубликованные элементы",
        examples=[
            Example(summary="Пример 1", value="true"),
            Example(summary="Пример 2", value="false"),
        ],
    ),
]


async def template_name_by_layout_dependency(layout: Layout) -> str:
    _layout = (
        CompetencyMatrixLayoutEnum(layout)
        if layout in CompetencyMatrixLayoutEnum
        else CompetencyMatrixLayoutEnum.LIST
    )
    match _layout:
        case CompetencyMatrixLayoutEnum.LIST:
            return "competency_matrix/blocks/items_list.html"
        case CompetencyMatrixLayoutEnum.GRID:
            return "competency_matrix/blocks/items_grid.html"
    msg = f"Not implemented template name for {_layout}"
    raise ValueError(msg)
