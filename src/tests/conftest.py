from typing import TYPE_CHECKING

import pytest
from litestar import Litestar
from litestar.testing import TestClient

from app.main import create_app

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(scope="session")
def test_app() -> Litestar:
    return create_app()


@pytest.fixture(scope="session")
def test_client(test_app: Litestar) -> "Generator[TestClient[Litestar], None, None]":
    with TestClient(app=test_app) as client:
        yield client
