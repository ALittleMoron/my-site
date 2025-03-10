import datetime

from behave.fixture import use_fixture_by_tag
from behave.model import Scenario

from tests.bdd.fixtures import (
    Context,
    get_competency_matrix_use_case,
    list_competency_matrix_use_case,
    list_sheets_use_case,
    list_subsections_use_case,
)
from tests.helpers.bdd import BddHelper
from tests.mocks.storage_mock import MockCompetencyMatrixStorage

fixtures = {
    "setup.use_case.get_competency_matrix_use_case": get_competency_matrix_use_case,
    "setup.use_case.list_competency_matrix_use_case": list_competency_matrix_use_case,
    "setup.use_case.list_sheets_use_case": list_sheets_use_case,
    "setup.use_case.list_subsections_use_case": list_subsections_use_case,
}


def before_scenario(context: Context, _: Scenario) -> None:
    context.bdd = BddHelper(context=context)
    context.storage = MockCompetencyMatrixStorage()
    context.current_datetime = datetime.datetime.now(tz=datetime.UTC)
    for tag in context.tags:
        if tag.startswith("setup.use_case"):
            context.use_case = use_fixture_by_tag(
                tag=tag,
                context=context,
                fixture_registry=fixtures,
            )
