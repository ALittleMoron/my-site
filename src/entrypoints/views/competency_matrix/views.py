from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import get
from litestar.di import Provide
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template

from core.competency_matrix.use_cases import AbstractListItemsUseCase, AbstractListSheetsUseCase
from entrypoints.views.competency_matrix.context_converters import CompetencyMatrixContextConverter
from entrypoints.views.competency_matrix.dependencies import (
    SheetName,
    template_name_by_layout_dependency,
)


@get("/sheets", description="Отображение списка листов матрицы компетенций")
async def sheets_handler(
    context_converter: FromDishka[CompetencyMatrixContextConverter],
    use_case: FromDishka[AbstractListSheetsUseCase],
) -> Template:
    sheets = await use_case.execute()
    return HTMXTemplate(
        template_name="competency_matrix/blocks/sheets.html",
        context=context_converter.from_competency_matrix_sheets(sheets=sheets),
    )


@get("/items", description="Отображение элементов матрицы компетенций")
async def matrix_elements_handler(
    sheet: SheetName,
    template_name: str,
    context_converter: FromDishka[CompetencyMatrixContextConverter],
    use_case: FromDishka[AbstractListItemsUseCase],
) -> Template:
    items = await use_case.execute(sheet_name=sheet)
    return HTMXTemplate(
        template_name=template_name,
        context=context_converter.from_competency_matrix_items(sheet=sheet, items=items),
    )


@get(
    "/",
    description="Отображение домашней страницы матрицы компетенций",
    name="competency-matrix-home-handler",
)
async def competency_matrix_home_handler() -> Template:
    return HTMXTemplate(template_name="competency_matrix/index.html", context={})


router = DishkaRouter(
    "/competency-matrix",
    route_handlers=[competency_matrix_home_handler, matrix_elements_handler, sheets_handler],
    dependencies={"template_name": Provide(template_name_by_layout_dependency)},
)
