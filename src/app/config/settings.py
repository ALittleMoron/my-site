from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class _AppSettings(BaseSettings):
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8080


class _DirSettings(BaseModel):
    root_path: Path = Path(__file__).parent.parent.parent.parent
    src_path: Path = root_path / "src"


class Settings(BaseSettings):
    app: _AppSettings = _AppSettings()
    dir: _DirSettings = _DirSettings()

    model_config = SettingsConfigDict(env_prefix='MY_SITE_', env_nested_delimiter="_")


settings = Settings()
