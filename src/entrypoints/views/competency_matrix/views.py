from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import get
from litestar.di import Provide
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.use_cases import (
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
    AbstractGetItemUseCase,
)
from entrypoints.views.competency_matrix.context_converters import CompetencyMatrixContextConverter
from entrypoints.views.competency_matrix.dependencies import (
    SheetName,
    template_name_by_layout_dependency,
)


@get(
    "/sheets",
    description="Отображение списка листов матрицы компетенций",
    name="competency-matrix-sheets-list-handler",
)
async def sheets_handler(
    context_converter: FromDishka[CompetencyMatrixContextConverter],
    use_case: FromDishka[AbstractListSheetsUseCase],
) -> Template:
    sheets = await use_case.execute()
    return HTMXTemplate(
        template_name="competency_matrix/blocks/sheets.html",
        context=context_converter.from_competency_matrix_sheets(sheets=sheets),
    )


@get(
    "/items",
    description="Отображение элементов матрицы компетенций",
    name="competency-matrix-items-list-handler",
)
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
    "/items/{pk:int}",
    description="Получение подробной информации о вопросе из матрицы компетенций.",
    name="competency-matrix-item-detail-handler",
)
async def get_competency_matrix_item_detail_handler(
    pk: int,
    use_case: FromDishka[AbstractGetItemUseCase],
    context_converter: FromDishka[CompetencyMatrixContextConverter],
) -> Template:
    try:
        item = await use_case.execute(item_id=pk)
    except CompetencyMatrixItemNotFoundError:
        return HTMXTemplate(
            template_name="competency_matrix/error_modal_item_not_found.html",
        )
    return HTMXTemplate(
        template_name="competency_matrix/blocks/item_detail.html",
        context=context_converter.from_competency_matrix_item(item=item),
    )


@get(
    "/prices",
    description="Отображение страницы матрицы компетенций со всеми вопросами",
    name="competency-matrix-prices-handler",
)
async def competency_matrix_prices_handler() -> Template:
    return HTMXTemplate(template_name="competency_matrix/index_prices.html", context={})


@get(
    "/questions",
    description="Отображение страницы матрицы компетенций со всеми вопросами",
    name="competency-matrix-questions-handler",
)
async def competency_matrix_questions_handler() -> Template:
    return HTMXTemplate(template_name="competency_matrix/index_questions.html", context={})


@get(
    "",
    description="Отображение домашней страницы матрицы компетенций",
    name="competency-matrix-index-handler",
)
async def competency_matrix_handler() -> Template:
    return HTMXTemplate(template_name="competency_matrix/index.html", context={})


router = DishkaRouter(
    "/competency-matrix",
    route_handlers=[
        competency_matrix_handler,
        competency_matrix_questions_handler,
        competency_matrix_prices_handler,
        matrix_elements_handler,
        get_competency_matrix_item_detail_handler,
        sheets_handler,
    ],
    dependencies={"template_name": Provide(template_name_by_layout_dependency)},
)
