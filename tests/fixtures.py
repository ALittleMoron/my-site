from collections.abc import Generator
from unittest.mock import patch

import pytest
from anydi import Container

from tests.client import SyncAndAsyncNinjaClient
from tests.helpers.api import APIHelper
from tests.helpers.app import AppHelper
from tests.helpers.factory import FactoryHelper


class FactoryFixture:
    factory: FactoryHelper

    @pytest.fixture(autouse=True)
    def _setup_factory(self) -> None:
        self.factory = FactoryHelper()


class ApiFixture:
    app: AppHelper
    api: APIHelper

    @pytest.fixture(autouse=True)
    def _setup_api(self, client: SyncAndAsyncNinjaClient, container: Container) -> Generator[None, None, None]:
        self.api = APIHelper(client=client)
        self.app = AppHelper(container=container)
        with patch("anydi.ext.django.container", container):
            yield
