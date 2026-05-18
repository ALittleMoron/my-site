import uuid
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from dishka import AsyncContainer, make_async_container
from dishka.integrations.litestar import LitestarProvider, setup_dishka
from litestar import Litestar
from litestar.testing import TestClient

from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser
from core.auth.types import RawToken
from core.types import IntId
from entrypoints.litestar.initializers import create_litestar_app
from infra.config.settings import Settings
from tests.unit.mocks.providers.account import MockUserAccountProvider
from tests.unit.mocks.providers.auth import MockAuthProvider
from tests.unit.mocks.providers.competency_matrix import MockCompetencyMatrixProvider
from tests.unit.mocks.providers.contacts import MockContactsProvider
from tests.unit.mocks.providers.files import MockFilesProvider
from tests.unit.mocks.providers.general import MockGeneralProvider


@pytest.fixture
def random_suffix(global_random_uuid: uuid.UUID) -> str:
    return global_random_uuid.hex[:8]


@pytest.fixture
def jwt_user() -> JwtUser:
    return JwtUser(username="test", role=RoleEnum.USER)


@pytest.fixture
def jwt_admin() -> JwtUser:
    return JwtUser(username="test", role=RoleEnum.ADMIN)


@pytest.fixture
def raw_token() -> RawToken:
    return RawToken("Bearer token")


@pytest_asyncio.fixture(loop_scope="function")
async def container(  # noqa: PLR0913
    test_settings: Settings,
    jwt_admin: JwtUser,
    raw_token: RawToken,
    global_random_uuid: uuid.UUID,
    global_random_int: IntId,
    random_suffix: str,
) -> AsyncGenerator[AsyncContainer]:
    container = make_async_container(
        LitestarProvider(),
        MockGeneralProvider(uuid_=global_random_uuid, int_=global_random_int),
        MockFilesProvider(random_suffix=random_suffix),
        MockCompetencyMatrixProvider(),
        MockContactsProvider(),
        MockUserAccountProvider(),
        MockAuthProvider(settings=test_settings, user=jwt_admin, raw_token=raw_token),
    )
    yield container
    await container.close()


@pytest.fixture
def app(container: AsyncContainer) -> Litestar:
    app = create_litestar_app(lifespan=[], container=container)
    setup_dishka(container=container, app=app)
    return app


@pytest.fixture
def no_auth_client(app: Litestar) -> Generator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def client(app: Litestar) -> Generator[TestClient]:
    with TestClient(app) as client:
        client.headers["Authorization"] = "Bearer ANY"
        yield client
