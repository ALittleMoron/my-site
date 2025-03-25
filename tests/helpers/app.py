from dataclasses import dataclass
from typing import Any

from anydi import Container

from core.competency_matrix.use_cases import ListSheetsUseCase
from tests.mocks.competency_matrix.use_cases import MockListSheetsUseCase


@dataclass(kw_only=True, frozen=True, slots=True)
class AppHelper:
    container: Container

    def override(self, interface: Any, instance: Any) -> None:
        self.container._override_instances[interface] = instance

    def override_list_sheets_use_case(self, use_case: MockListSheetsUseCase) -> None:
        self.override(ListSheetsUseCase, use_case)
