from behave.fixture import use_fixture_by_tag
from behave.model import Scenario, Table
from behave.runner import Context as BaseContext

from tests.helpers.bdd import BddHelper

fixtures = {}


class Context(BaseContext):
    table: Table
    tags: list[str]
    bdd: BddHelper


def before_scenario(context: Context, _: Scenario) -> None:
    context.bdd = BddHelper()
    for tag in context.tags:
        if tag.startswith("setup.use_case"):
            context.use_case = use_fixture_by_tag(
                tag=tag,
                context=context,
                fixture_registry=fixtures,
            )
