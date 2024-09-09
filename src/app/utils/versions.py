import tomllib

from app.config import settings


def get_app_version() -> str:
    with (settings.dir.root_path / "pyproject.toml").open('rb') as reader:
        project_metadata = tomllib.load(reader)
    try:
        return project_metadata["project"]["version"]
    except KeyError:
        return '1.0.0'
