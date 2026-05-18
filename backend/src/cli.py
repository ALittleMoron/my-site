from litestar import Litestar

from entrypoints.litestar.initializers import create_cli_app
from entrypoints.litestar.lifespan import app_lifespan


def create_cli() -> Litestar:
    return create_cli_app(lifespan=[app_lifespan])
