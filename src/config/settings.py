import os
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.constants import constants

ENV_TYPE = os.environ.get("ENV_TYPE", "DEV").upper()
match ENV_TYPE:
    case "DEV":
        env_file_name = ".env.dev"
    case "LOCAL":
        env_file_name = ".env.local"
    case _:
        env_file_name = ".env"
env_file_path = constants.dir.root_path / env_file_name


class _AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=env_file_path,
        extra="ignore",
    )

    debug: bool = True
    secret_key: SecretStr = SecretStr("SECRET_KEY")
    domain: str = "localhost"
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000


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


class Settings:
    app: _AppSettings = _AppSettings()
    auth: _AuthSettings = _AuthSettings()
    database: _DatabaseSettings = _DatabaseSettings()
    minio: _MinioSettings = _MinioSettings()

    @property
    def minio_url(self) -> str:
        is_local_domain = self.app.domain in {"localhost", "127.0.0.1", "0.0.0.0"}  # noqa: S104
        schema = "http" if is_local_domain else "https"
        return f"{schema}://{self.app.domain}"

    def get_minio_object_url(self, bucket: Literal["media", "static"], object_path: str) -> str:
        object_path = object_path.removeprefix("/")
        return f"{self.minio_url}/{bucket}/{object_path}"


settings = Settings()
