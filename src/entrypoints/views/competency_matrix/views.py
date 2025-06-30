from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import get
from litestar.di import Provide
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template

from core.competency_matrix.use_cases import AbstractListItemsUseCase
from entrypoints.views.competency_matrix.context_converters import CompetencyMatrixContextConverter
from entrypoints.views.competency_matrix.dependencies import (
    competency_matrix_layout_dependency,
    template_name_by_layout_dependency,
    sheet_name_dependency,
)


@get("", description="Отображение элементов матрицы компетенций")
async def matrix_elements(
    sheet: str,
    template_name: str,
    context_converter: FromDishka[CompetencyMatrixContextConverter],
    use_case: FromDishka[AbstractListItemsUseCase],
) -> Template:
    items = await use_case.execute(sheet_name=sheet)
    return HTMXTemplate(
        template_name=template_name,
        context=context_converter.from_competency_matrix_items(sheet=sheet, items=items),
    )


router = DishkaRouter(
    "/competency-matrix/",
    route_handlers=[matrix_elements],
    dependencies={
        "sheet": Provide(sheet_name_dependency),
        "layout": Provide(competency_matrix_layout_dependency),
        "template_name": Provide(template_name_by_layout_dependency),
    },
)
