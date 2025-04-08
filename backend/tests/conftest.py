import os
from collections.abc import Generator
from typing import cast

import pytest
from anydi import Container
from anydi.ext.django.apps import ContainerConfig
from django.apps.registry import apps
from ninja import NinjaAPI

from api.routers import api
from tests.client import SyncAndAsyncNinjaClient


@pytest.fixture(scope="session")
def app() -> NinjaAPI:
    os.environ["NINJA_SKIP_REGISTRY"] = "yes"
    return api


@pytest.fixture(scope="session")
def client(app: NinjaAPI) -> SyncAndAsyncNinjaClient:
    return SyncAndAsyncNinjaClient(app)


@pytest.fixture
def test_container() -> Generator[Container, None, None]:
    app_config = cast(ContainerConfig, apps.get_app_config(ContainerConfig.label))
    app_config.container._testing = True  # noqa: SLF001
    yield app_config.container
    app_config.container._testing = False  # noqa: SLF001
