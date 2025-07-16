from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import get
from litestar.di import Provide
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template

from config.settings import settings
from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.use_cases import (
    AbstractGetItemUseCase,
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
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
    cache=settings.app.get_cache_duration(120),  # 2 минуты
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
    cache=settings.app.get_cache_duration(60),  # 1 минута
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
        context=context_converter.context_from_competency_matrix_items(sheet=sheet, items=items),
    )


@get(
    "/items/{pk:int}",
    description="Получение подробной информации о вопросе из матрицы компетенций.",
    name="competency-matrix-item-detail-handler",
    cache=settings.app.get_cache_duration(15),  # 15 секунд
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
        context=context_converter.context_from_competency_matrix_item(item=item),
    )


@get(
    "",
    description="Отображение домашней страницы матрицы компетенций",
    name="competency-matrix-questions-handler",
    cache=settings.app.get_cache_duration(600),  # 10 минут
)
async def competency_matrix_handler() -> Template:
    return HTMXTemplate(template_name="competency_matrix/index.html", context={})


router = DishkaRouter(
    "/competency-matrix",
    route_handlers=[
        competency_matrix_handler,
        matrix_elements_handler,
        get_competency_matrix_item_detail_handler,
        sheets_handler,
    ],
    dependencies={"template_name": Provide(template_name_by_layout_dependency)},
)
