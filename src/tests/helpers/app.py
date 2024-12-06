from contextlib import contextmanager
from dataclasses import dataclass

from litestar import Litestar

from tests.mocks.use_cases.list_competency_matrix_items import MockListCompetencyMatrixItems


@dataclass
class AppHelper:
    app: Litestar

    @contextmanager
    def clean_list_competency_matrix_items_use_case(
        self,
        use_case: MockListCompetencyMatrixItems,
    ) -> None:
        yield
        use_case.items = []
