from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.configs import _DirConstants


class _AppSettings(BaseSettings):
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8080
    debug: bool = False

    model_config = SettingsConfigDict(env_prefix='APP_', env_nested_delimiter="_")


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
    dir: _DirConstants = _DirConstants()
    database: _DatabaseSettings = _DatabaseSettings()


settings = Settings()
