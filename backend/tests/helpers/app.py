from collections.abc import Generator
from dataclasses import dataclass

from anydi import Container

from core.competency_matrix.use_cases import ListItemsUseCase, ListSheetsUseCase, GetItemUseCase
from tests.mocks.competency_matrix.use_cases import (
    MockListItemsUseCase,
    MockListSheetsUseCase,
    MockGetItemUseCase,
)


@dataclass(kw_only=True, frozen=True, slots=True)
class AppHelper:
    container: Container

    def override_list_sheets_use_case(
        self,
        use_case: MockListSheetsUseCase,
    ) -> Generator[None, None, None]:
        with self.container.override(ListSheetsUseCase, use_case):
            yield

    def override_list_competency_matrix_items(
        self,
        use_case: MockListItemsUseCase,
    ) -> Generator[None, None, None]:
        with self.container.override(ListItemsUseCase, use_case):
            yield

    def override_get_competency_matrix_item(
        self,
        use_case: MockGetItemUseCase,
    ) -> Generator[None, None, None]:
        with self.container.override(GetItemUseCase, use_case):
            yield
