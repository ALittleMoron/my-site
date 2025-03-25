import os

import pytest
from anydi import Container
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


@pytest.fixture(scope="function")
def container() -> Container:
    return Container(testing=True)