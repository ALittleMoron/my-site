from behave import given, then, when
from behave.api.async_step import async_run_until_complete

from app.core.competency_matrix.schemas import (
    FullFilledCompetencyMatrixItem,
)
from app.core.competency_matrix.use_cases import GetItemUseCase
from app.core.exceptions import EntryNotFoundError
from tests.bdd.fixtures import Context as BaseContext


class Context(BaseContext):
    use_case: GetItemUseCase
    raise_exception: Exception | None
    item: FullFilledCompetencyMatrixItem


@given("Список компетенций")
def given_grades(context: Context) -> None:
    for grade in context.bdd.parse_grades():
        context.storage.grades[grade.id] = grade


@given("Список дополнительных ресурсов у вопроса {item_id:d}")
@async_run_until_complete
async def given_resources(context: Context, item_id: int) -> None:
    item = await context.storage.get_competency_matrix_item(item_id=item_id)
    for resource in context.bdd.parse_resources():
        context.storage.resources[item_id].append(resource)
        item.resources.values.append(resource)


@when("Получаем вопроса {item_id:d} из матрицы компетенций")
@async_run_until_complete
async def when_get_items_list_by_sheet_id(context: Context, item_id: int) -> None:
    context.raise_exception = None
    try:
        context.item = await context.use_case.execute(item_id=item_id)
    except EntryNotFoundError as exc:
        context.raise_exception = exc


@then("Полученный вопрос из матрицы компетенций")
def then_assert_item_detail(context: Context) -> None:
    expected_item = context.bdd.parse_full_filled_competency_matrix_item()
    actual_item = context.item
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
        actual=actual_item.answer,
        expected=expected_item.answer,
        msg="competency_matrix_item.answer",
    )
    context.bdd.assert_equal(
        actual=actual_item.interview_expected_answer,
        expected=expected_item.interview_expected_answer,
        msg="competency_matrix_item.interview_expected_answer",
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
        actual=actual_item.grade,
        expected=expected_item.grade,
        msg="competency_matrix_item.grade",
    )
    context.bdd.assert_equal(
        actual=actual_item.subsection_id,
        expected=expected_item.subsection_id,
        msg="competency_matrix_item.subsection_id",
    )
    context.bdd.assert_equal(
        actual=actual_item.subsection,
        expected=expected_item.subsection,
        msg="competency_matrix_item.subsection",
    )


@then("Полученный список дополнительных ресурсов к вопросу {item_id:d}")
@async_run_until_complete
async def then_assert_item_resources(context: Context, item_id: int) -> None:
    actual_item = await context.storage.get_competency_matrix_item(item_id=item_id)
    actual_resources = actual_item.resources.values
    expected_resources = context.bdd.parse_resources()
    context.bdd.assert_equal(
        actual=len(actual_resources),
        expected=len(expected_resources),
        msg="actual competency matrix item resources count not suit expected",
    )
    for actual, expected in zip(actual_resources, expected_resources, strict=True):
        context.bdd.assert_equal(
            actual=actual.id,
            expected=expected.id,
            msg="resource.id",
        )
        context.bdd.assert_equal(
            actual=actual.name,
            expected=expected.name,
            msg="resource.name",
        )
        context.bdd.assert_equal(
            actual=actual.url,
            expected=expected.url,
            msg="resource.url",
        )
        context.bdd.assert_equal(
            actual=actual.context,
            expected=expected.context,
            msg="resource.context",
        )
