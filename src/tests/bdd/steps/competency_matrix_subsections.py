from behave import given, then, when
from behave.api.async_step import async_run_until_complete

from app.core.competency_matrix.schemas import ListSubsectionsParams, Subsections
from app.core.competency_matrix.use_cases import ListSubsectionsUseCase
from tests.bdd.fixtures import Context as BaseContext


class Context(BaseContext):
    use_case: ListSubsectionsUseCase
    subsections: Subsections


@given("Список подразделов")
def given_subsections(context: Context) -> None:
    for subsection in context.bdd.parse_subsections():
        context.storage.subsections[subsection.id] = subsection
        context.storage.sections[subsection.section.id] = subsection.section
        context.storage.sheets[subsection.section.sheet.id] = subsection.section.sheet


@when("Получаем список подразделов к вопросам по листу {sheet_id:d}")
@async_run_until_complete
async def when_get_subsections_list_by_sheet_id(context: Context, sheet_id: int) -> None:
    context.subsections = await context.use_case.execute(
        params=ListSubsectionsParams(sheet_id=sheet_id),
    )


@when("Получаем список подразделов к вопросам")
@async_run_until_complete
async def when_get_subsections_list(context: Context) -> None:
    context.subsections = await context.use_case.execute(
        params=ListSubsectionsParams(sheet_id=None),
    )


@then("Полученный список подразделов к вопросам матрицы компетенций")
def then_assert_subsections_list(context: Context) -> None:
    expected_subsections = context.bdd.parse_subsections()
    context.bdd.assert_equal(
        actual=len(context.subsections),
        expected=len(expected_subsections),
        msg="actual competency matrix subsections count not suit expected",
    )
    for actual_item, expected_item in zip(context.subsections, expected_subsections, strict=True):
        context.bdd.assert_equal(
            actual=actual_item.id,
            expected=expected_item.id,
            msg="subsection.id",
        )
        context.bdd.assert_equal(
            actual=actual_item.name,
            expected=expected_item.name,
            msg="subsection.name",
        )
