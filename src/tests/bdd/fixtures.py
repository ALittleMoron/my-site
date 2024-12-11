import datetime

from behave.model import Table
from behave.runner import Context as BaseContext

from app.core.competency_matrix.use_cases import (
    ListCompetencyMatrixItemsUseCase,
    ListSheetsUseCase,
    ListSubsectionsUseCase,
)
from tests.helpers.bdd import BddHelper
from tests.mocks.storage_mock import MockCompetencyMatrixStorage


class Context(BaseContext):
    table: Table
    tags: list[str]
    bdd: BddHelper
    storage: MockCompetencyMatrixStorage
    current_datetime: datetime.datetime


def list_competency_matrix_use_case(context: Context) -> ListCompetencyMatrixItemsUseCase:
    return ListCompetencyMatrixItemsUseCase(storage=context.storage)


def list_sheets_use_case(context: Context) -> ListSheetsUseCase:
    return ListSheetsUseCase(storage=context.storage)


def list_subsections_use_case(context: Context) -> ListSubsectionsUseCase:
    return ListSubsectionsUseCase(storage=context.storage)
