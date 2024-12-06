from collections.abc import Mapping, Sequence  # noqa
from typing import TYPE_CHECKING

import pytest
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import TestClient
from litestar.types import ControllerRouterHandler  # noqa

from app.main import create_app, get_plugins
from tests.mocks.storage_mock import MockStorage
from tests.mocks.use_cases.list_competency_matrix_items import MockListCompetencyMatrixItems
from tests.utils import provide_async

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(scope="session")
def mock_storage() -> MockStorage:
    return MockStorage()


@pytest.fixture(scope="session")
def mock_list_competency_matrix_items_use_case() -> MockListCompetencyMatrixItems:
    return MockListCompetencyMatrixItems()


@pytest.fixture(scope="session")
def app_dependencies(
    mock_storage: MockStorage,
    mock_list_competency_matrix_items_use_case: MockListCompetencyMatrixItems,
) -> Mapping[str, Provide]:
    return {
        'storage': provide_async(mock_storage),
        'list_competency_matrix_items_use_case': provide_async(
            mock_list_competency_matrix_items_use_case,
        ),
    }


@pytest.fixture(scope="session")
def test_app(app_dependencies: Mapping[str, Provide]) -> Litestar:
    return create_app(debug=True, plugins=get_plugins(), deps=app_dependencies)


@pytest.fixture(scope="session")
def test_client(test_app: Litestar) -> "Generator[TestClient[Litestar], None, None]":
    with TestClient(app=test_app) as client:
        yield client
