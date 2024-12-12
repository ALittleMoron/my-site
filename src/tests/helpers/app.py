from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field

from litestar import Litestar
from litestar.di import Provide
from litestar.handlers import HTTPRouteHandler
from litestar.testing import TestClient

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

    @staticmethod
    def get_mocked_handler(
        handler: HTTPRouteHandler,
        override_dependencies: Mapping[str, Provide],
    ) -> HTTPRouteHandler:
        handler_copy = deepcopy(handler)
        for key, value in override_dependencies.items():
            (handler_copy.dependencies or {})[key] = value  # type: ignore[index]
        return handler_copy

    def create_list_competency_matrix_items_client(
        self,
        use_case: MockListCompetencyMatrixItemsUseCase,
    ) -> TestClient[Litestar]:
        return create_mocked_test_client(  # type: ignore[no-any-return]
            handler=self.get_mocked_handler(
                handler=list_competency_matrix_items_handler,
                override_dependencies={"use_case": provide_async(use_case)},
            ),
            base_url=self.merge_url("/items/"),
        )

    def create_list_competency_matrix_sheets_client(
        self,
        use_case: MockListSheetsUseCase,
    ) -> TestClient[Litestar]:
        return create_mocked_test_client(  # type: ignore[no-any-return]
            handler=self.get_mocked_handler(
                handler=list_competency_matrix_sheet_handler,
                override_dependencies={"use_case": provide_async(use_case)},
            ),
            base_url=self.merge_url('/sheets/'),
        )

    def create_list_competency_matrix_subsections_client(
        self,
        use_case: MockListSubsectionsUseCase,
    ) -> TestClient[Litestar]:
        return create_mocked_test_client(  # type: ignore[no-any-return]
            handler=self.get_mocked_handler(
                handler=list_competency_matrix_subsection_handler,
                override_dependencies={"use_case": provide_async(use_case)},
            ),
            base_url=self.merge_url('/subsections/'),
        )
