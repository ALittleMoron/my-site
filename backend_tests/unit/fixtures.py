import pytest
from dishka import AsyncContainer
from litestar.testing import TestClient

from backend_tests.fixtures import FactoryFixture
from backend_tests.helpers.api import APIHelper
from backend_tests.helpers.app import IocContainerHelper

__all__ = ["ApiFixture", "ContainerFixture", "FactoryFixture"]


class ContainerFixture:
    container: IocContainerHelper

    @pytest.fixture(autouse=True)
    def _setup_app(
        self,
        container: AsyncContainer,
    ) -> None:
        self.container = IocContainerHelper(container=container)


class ApiFixture:
    api: APIHelper

    @pytest.fixture(autouse=True)
    def _setup_api(
        self,
        client: TestClient,
        no_auth_client: TestClient,
    ) -> None:
        self.api = APIHelper(client=client)
        self.no_auth_api = APIHelper(client=no_auth_client)
