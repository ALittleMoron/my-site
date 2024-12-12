from behave import given, then, when
from behave.api.async_step import async_run_until_complete

from app.core.competency_matrix.schemas import (
    FilledCompetencyMatrixItems,
    ListItemsParams,
)
from app.core.competency_matrix.use_cases import ListItemsUseCase
from tests.bdd.fixtures import Context as BaseContext


class Context(BaseContext):
    use_case: ListItemsUseCase
    short_items: FilledCompetencyMatrixItems


@given("Список разделов")
def given_sections(context: Context) -> None:
    for section in context.bdd.parse_sections():
        context.storage.sections[section.id] = section
        context.storage.sheets[section.sheet.id] = section.sheet


@given("Список вопросов в матрице компетенций")
def given_items(context: Context) -> None:
    for item in context.bdd.parse_short_competency_matrix_items():
        context.storage.short_competency_matrix_items[item.id] = item


@when("Получаем список вопросов из матрицы компетенций по листу {sheet_id:d}")
@async_run_until_complete
async def when_get_items_list_by_sheet_id(context: Context, sheet_id: int) -> None:
    context.short_items = await context.use_case.execute(
        params=ListItemsParams(sheet_id=sheet_id),
    )


@when("Получаем список вопросов из матрицы компетенций")
@async_run_until_complete
async def when_get_items_list(context: Context) -> None:
    context.short_items = await context.use_case.execute(
        params=ListItemsParams(sheet_id=None),
    )


@then("Полученный список вопросов матрицы компетенций")
def then_assert_items_list(context: Context) -> None:
    expected_items = context.bdd.parse_short_filled_competency_matrix_items()
    context.bdd.assert_equal(
        actual=len(context.short_items),
        expected=len(expected_items),
        msg="actual competency matrix items count not suit expected",
    )
    for actual_item, expected_item in zip(context.short_items, expected_items, strict=True):
        context.bdd.assert_equal(
            actual=actual_item.id,
            expected=expected_item.id,
            msg="competency_matrix_item.id",
        )
        context.bdd.assert_equal(
            actual=actual_item.question,
            expected=expected_item.question,
            msg="competency_matrix_item.question",
        )
        context.bdd.assert_equal(
            actual=actual_item.status,
            expected=expected_item.status,
            msg="competency_matrix_item.status",
        )
        context.bdd.assert_equal(
            actual=actual_item.status_changed,
            expected=expected_item.status_changed,
            msg="competency_matrix_item.status_changed",
        )
        context.bdd.assert_equal(
            actual=actual_item.grade_id,
            expected=expected_item.grade_id,
            msg="competency_matrix_item.grade_id",
        )
        context.bdd.assert_equal(
            actual=actual_item.subsection_id,
            expected=expected_item.subsection_id,
            msg="competency_matrix_item.subsection_id",
        )
