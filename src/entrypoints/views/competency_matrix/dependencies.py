from typing import Annotated

from litestar.openapi.spec.example import Example
from litestar.params import Parameter

from entrypoints.views.competency_matrix.enums import CompetencyMatrixLayoutEnum

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


async def sheet_name_dependency(sheet: SheetName) -> str:
    return sheet


async def competency_matrix_layout_dependency(layout_: Layout) -> CompetencyMatrixLayoutEnum:
    if layout_ in CompetencyMatrixLayoutEnum:
        return CompetencyMatrixLayoutEnum(layout_)
    return CompetencyMatrixLayoutEnum.LIST


async def template_name_by_layout_dependency(
    competency_matrix_layout: CompetencyMatrixLayoutEnum,
) -> str:
    match competency_matrix_layout:
        case CompetencyMatrixLayoutEnum.LIST:
            return "competency_matrix/list.html"
        case CompetencyMatrixLayoutEnum.GRID:
            return "competency_matrix/grid.html"
    msg = f"Not implemented template name for {competency_matrix_layout}"
    raise ValueError(msg)
