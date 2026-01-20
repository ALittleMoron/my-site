from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, Request, get
from litestar.datastructures import State
from litestar.di import Provide
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template

from config.settings import settings
from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.use_cases import (
    AbstractGetItemUseCase,
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
)
from core.types import IntId
from entrypoints.litestar.views.competency_matrix.context_converters import (
    CompetencyMatrixContextConverter,
)
from entrypoints.litestar.views.competency_matrix.dependencies import (
    OnlyPublished,
    SheetName,
    template_name_by_layout_dependency,
)


class CompetencyMatrixViewController(Controller):
    path = "/competency-matrix"

    @get(
        "/filters-block",
        description="Отображение блока фильтров",
        name="competency-matrix-filters-block-handler",
        cache=settings.app.get_cache_duration(120),  # 2 минуты
    )
    async def filters_block(self) -> Template:
        return HTMXTemplate(template_name="competency_matrix/blocks/filters.html")

    @get(
        "/sheets",
        description="Отображение списка листов матрицы компетенций",
        name="competency-matrix-sheets-list-handler",
        cache=settings.app.get_cache_duration(120),  # 2 минуты
    )
    async def sheets(
        self,
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
        dependencies={"template_name": Provide(template_name_by_layout_dependency)},
    )
    async def matrix_elements(  # noqa: PLR0913
        self,
        request: Request[JwtUser, Token, State],
        sheet: SheetName,
        only_published: OnlyPublished,
        template_name: str,
        context_converter: FromDishka[CompetencyMatrixContextConverter],
        use_case: FromDishka[AbstractListItemsUseCase],
    ) -> Template:
        if not request.user.is_admin and not only_published:
            only_published = True
        items = await use_case.execute(sheet_name=sheet, only_published=only_published)
        return HTMXTemplate(
            template_name=template_name,
            context=context_converter.context_from_competency_matrix_items(
                sheet=sheet,
                items=items,
            ),
        )

    @get(
        "/items/{pk:int}",
        description="Получение подробной информации о вопросе из матрицы компетенций.",
        name="competency-matrix-item-detail-handler",
        cache=settings.app.get_cache_duration(15),  # 15 секунд
    )
    async def get_competency_matrix_item_detail(
        self,
        pk: int,
        request: Request[JwtUser, Token, State],
        use_case: FromDishka[AbstractGetItemUseCase],
        context_converter: FromDishka[CompetencyMatrixContextConverter],
    ) -> Template:
        only_published = not request.user.is_admin
        try:
            item = await use_case.execute(item_id=IntId(pk), only_published=only_published)
        except CompetencyMatrixItemNotFoundError:
            template_name = "competency_matrix/blocks/error_modal_item_not_found.html"
            return HTMXTemplate(template_name=template_name)
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
    async def competency_matrix(self) -> Template:
        return HTMXTemplate(template_name="competency_matrix/index.html")


router = DishkaRouter("", route_handlers=[CompetencyMatrixViewController])
