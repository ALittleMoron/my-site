from dataclasses import dataclass, field

from litestar import Litestar
from litestar.di import Provide
from litestar.testing import TestClient

from app.api.competency_matrix.deps import (
    build_competency_matrix_list_items_params,
    build_competency_matrix_subsections_params,
)
from app.api.competency_matrix.endpoints import (
    list_competency_matrix_items_handler,
    list_competency_matrix_sheet_handler,
    list_competency_matrix_subsection_handler,
)
from tests.mocks.use_cases.list_competency_matrix_items import MockListCompetencyMatrixItemsUseCase
from tests.mocks.use_cases.list_competency_matrix_sheets import MockListSheetsUseCase
from tests.mocks.use_cases.list_competency_matrix_subsections import MockListSubsectionsUseCase
from tests.utils import create_mocked_test_client, provide_async


@dataclass(kw_only=True)
class AppHelper:
    domain: str = field(default="http://testserver.local")

    def merge_url(self, url: str) -> str:
        return f"{self.domain.rstrip('/')}/{url.lstrip('/')}"

    def create_list_competency_matrix_items_client(
        self,
        use_case: MockListCompetencyMatrixItemsUseCase,
    ) -> TestClient[Litestar]:
        return create_mocked_test_client(
            handler=list_competency_matrix_items_handler,
            dependencies={
                'list_competency_matrix_items_params': Provide(
                    build_competency_matrix_list_items_params,
                ),
                'list_competency_matrix_items_use_case': provide_async(use_case),
            },
            base_url=self.merge_url("/items/"),
        )

    def create_list_competency_matrix_sheets_client(
        self,
        use_case: MockListSheetsUseCase,
    ) -> TestClient[Litestar]:
        return create_mocked_test_client(
            handler=list_competency_matrix_sheet_handler,
            dependencies={'list_competency_matrix_sheets_use_case': provide_async(use_case)},
            base_url=self.merge_url('/sheets/'),
        )

    def create_list_competency_matrix_subsections_client(
        self,
        use_case: MockListSubsectionsUseCase,
    ) -> TestClient[Litestar]:
        return create_mocked_test_client(
            handler=list_competency_matrix_subsection_handler,
            dependencies={
                'list_competency_matrix_subsections_params': Provide(
                    build_competency_matrix_subsections_params,
                ),
                'list_competency_matrix_subsections_use_case': provide_async(use_case),
            },
            base_url=self.merge_url('/subsections/'),
        )
