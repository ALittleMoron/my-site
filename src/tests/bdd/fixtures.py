import datetime

from behave.model import Table
from behave.runner import Context as BaseContext

from app.core.competency_matrix.use_cases import ListCompetencyMatrixItemsUseCase
from tests.helpers.bdd import BddHelper
from tests.mocks.storage_mock import MockStorage


class Context(BaseContext):
    table: Table
    tags: list[str]
    bdd: BddHelper
    storage: MockStorage
    current_datetime: datetime.datetime


def list_competency_matrix_use_case(context: Context) -> ListCompetencyMatrixItemsUseCase:
    return ListCompetencyMatrixItemsUseCase(storage=context.storage)
