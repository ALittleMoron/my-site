from behave import given

from tests.bdd.fixtures import Context as BaseContext


class Context(BaseContext): ...


@given("Список разделов")
def given_sections(context: Context) -> None:
    for section in context.bdd.parse_sections():
        context.storage.sections[section.id] = section
        context.storage.sheets[section.sheet.id] = section.sheet
