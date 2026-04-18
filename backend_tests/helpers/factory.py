from dataclasses import dataclass
from functools import cached_property

from backend_tests.helpers.factories.api import ApiFactoryHelper
from backend_tests.helpers.factories.core import CoreFactoryHelper


@dataclass(kw_only=True, frozen=True)
class FactoryHelper:
    @cached_property
    def core(self) -> CoreFactoryHelper:
        return CoreFactoryHelper()

    @cached_property
    def api(self) -> ApiFactoryHelper:
        return ApiFactoryHelper()
