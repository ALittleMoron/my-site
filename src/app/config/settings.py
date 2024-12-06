from pathlib import Path

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class _AppSettings(BaseSettings):
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8080
    debug: bool = False

    model_config = SettingsConfigDict(env_prefix='APP_', env_nested_delimiter="_")


class _DirSettings(BaseModel):
    root_path: Path = Path(__file__).parent.parent.parent.parent
    src_path: Path = root_path / "src"


class _DatabaseSettings(BaseSettings):
    protocol: str = "postgresql+psycopg_async"
    user: str = "postgres"
    password: SecretStr = SecretStr("postgres")
    host: str = "localhost"
    port: str = "5432"
    name: str = "my_site_database"

    model_config = SettingsConfigDict(env_prefix='DB_', env_nested_delimiter="_")

    @property
    def domain(self) -> SecretStr:
        return SecretStr(
            f"{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}",
        )

    @property
    def url(self) -> SecretStr:
        return SecretStr(f"{self.protocol}://{self.domain.get_secret_value()}")


class Settings(BaseSettings):
    app: _AppSettings = _AppSettings()
    dir: _DirSettings = _DirSettings()
    database: _DatabaseSettings = _DatabaseSettings()


settings = Settings()
