from behave import given, then, when
from behave.api.async_step import async_run_until_complete

from app.core.competency_matrix.schemas import Sheets
from app.core.competency_matrix.use_cases import ListSheetsUseCase
from tests.bdd.fixtures import Context as BaseContext


class Context(BaseContext):
    use_case: ListSheetsUseCase
    sheets: Sheets


@given("Список листов с вопросами")
def given_sheets(context: Context) -> None:
    for sheet in context.bdd.parse_sheets():
        context.storage.sheets[sheet.id] = sheet


@when("Получаем список листов с вопросами")
@async_run_until_complete
async def when_get_sheets_list(context: Context) -> None:
    context.sheets = await context.use_case.execute()


@then("Полученный список листов с вопросами матрицы компетенций")
def then_assert_sheets_list(context: Context) -> None:
    expected_items = context.bdd.parse_sheets()
    context.bdd.assert_equal(
        actual=len(context.sheets),
        expected=len(expected_items),
        msg="actual competency matrix sheets count not suit expected",
    )
    for actual_item, expected_item in zip(context.sheets, expected_items, strict=True):
        context.bdd.assert_equal(
            actual=actual_item.id,
            expected=expected_item.id,
            msg="sheet.id",
        )
        context.bdd.assert_equal(
            actual=actual_item.name,
            expected=expected_item.name,
            msg="sheet.name",
        )
