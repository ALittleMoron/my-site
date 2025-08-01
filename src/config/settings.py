from typing import Literal

from litestar.config.response_cache import CACHE_FOREVER
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.constants import constants

env_file_path = constants.dir.root_path / ".env"


class _AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=env_file_path,
        extra="ignore",
    )

    debug: bool = True
    secret_key: SecretStr = SecretStr("SECRET_KEY")
    domain: str = "localhost"
    use_cache: bool = True
    use_rate_limit: bool = True

    @property
    def is_local_domain(self) -> bool:
        return self.domain in {"localhost", "127.0.0.1", "0.0.0.0"}  # noqa: S104

    def get_cache_duration(
        self,
        value: bool | int | type[CACHE_FOREVER],  # noqa: FBT001
    ) -> bool | int | type[CACHE_FOREVER]:
        if self.use_cache:
            return value
        return 0


class _DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=env_file_path,
        extra="ignore",
    )

    # connection creds settings
    user: str = "postgres"
    password: SecretStr = SecretStr("postgres")
    driver: str = "postgresql+psycopg"
    host: str = "localhost"
    port: str = "5432"
    name: str = "my_site_database"

    # engine_settings
    pool_pre_ping: bool = True
    pool_size: int = 10
    max_overflow: int = 20

    # session maker settings
    expire_on_commit: bool = False

    @property
    def url(self) -> SecretStr:
        return SecretStr(
            f"{self.driver}://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}",
        )


class _AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTH_",
        env_file=env_file_path,
        extra="ignore",
    )

    token_expire_seconds: int = 60 * 60 * 24 * 2
    crypto_scheme: str = "bcrypt"


class _MinioSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MINIO_",
        env_file=env_file_path,
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 9000
    secret_key: SecretStr = SecretStr("minioadmin")
    access_key: str = "minioadmin"
    secure: bool = False

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"


class _SentrySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SENTRY_",
        env_file=env_file_path,
        extra="ignore",
    )

    dsn: str = ""


class Settings:
    app: _AppSettings = _AppSettings()
    auth: _AuthSettings = _AuthSettings()
    database: _DatabaseSettings = _DatabaseSettings()
    minio: _MinioSettings = _MinioSettings()
    sentry: _SentrySettings = _SentrySettings()

    @property
    def base_url(self) -> str:
        url_schema = "http" if self.app.is_local_domain else "https"
        postfix = ":8000" if self.app.debug and self.app.is_local_domain else ""
        return f"{url_schema}://{self.app.domain}{postfix}"

    def get_minio_object_url(self, bucket: Literal["media", "static"], object_path: str) -> str:
        return f"{self.base_url}/{bucket}/{object_path.removeprefix('/')}"

    def get_url(self, path: str) -> str:
        return f"{self.base_url}/{path.removeprefix('/')}"


settings = Settings()
