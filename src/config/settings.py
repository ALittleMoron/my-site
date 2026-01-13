from litestar.config.response_cache import CACHE_FOREVER
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.constants import constants
from core.files.types import Namespace
from core.schemas import Secret


class SecretStrExtended(SecretStr):
    def to_domain_secret(self) -> Secret[str]:
        return Secret(self.get_secret_value())


class _ProjectBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=constants.path.env_file, extra="ignore")


class _AppSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    debug: bool = True
    secret_key: SecretStrExtended = SecretStrExtended("SECRET_KEY")
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


class _AdminSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="ADMIN_")

    init_username: str = "admin"
    init_password: SecretStrExtended = SecretStrExtended("admin")


class _DatabaseSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    # connection creds settings
    user: str = "postgres"
    password: SecretStrExtended = SecretStrExtended("postgres")
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
    def url(self) -> SecretStrExtended:
        return SecretStrExtended(
            f"{self.driver}://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}",
        )


class _AuthSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_")

    public_key: SecretStrExtended
    private_key: SecretStrExtended
    token_expire_seconds: int = 60 * 60 * 24 * 2


class _MinioSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="MINIO_")

    host: str = "localhost"
    port: int = 9000
    secret_key: SecretStrExtended = SecretStrExtended("minioadmin")
    access_key: str = "minioadmin"
    secure: bool = False
    presign_put_expires_seconds: int = 60 * 5  # 5 minutes

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"


class _SentrySettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="SENTRY_")

    dsn: str = ""


class _ValkeySettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="VALKEY_")

    host: str = "localhost"
    port: int = 6379

    def get_url(self, db: int | str) -> SecretStrExtended:
        return SecretStrExtended(f"valkey://{self.host}:{self.port}/{db}")

    @property
    def url_for_http_cache(self) -> SecretStrExtended:
        return self.get_url(db=constants.valkey.databases.response_cache)


class Settings:
    app: _AppSettings = _AppSettings()
    admin: _AdminSettings = _AdminSettings()
    auth: _AuthSettings = _AuthSettings()
    database: _DatabaseSettings = _DatabaseSettings()
    minio: _MinioSettings = _MinioSettings()
    sentry: _SentrySettings = _SentrySettings()
    valkey: _ValkeySettings = _ValkeySettings()

    @property
    def base_url(self) -> str:
        url_schema = "http" if self.app.is_local_domain else "https"
        postfix = ":8000" if self.app.debug and self.app.is_local_domain else ""
        return f"{url_schema}://{self.app.domain}{postfix}"

    def get_minio_object_url(self, object_path: str, bucket: Namespace) -> str:
        url_schema = "http" if self.app.is_local_domain else "https"
        base_url = (
            f"{url_schema}://{self.minio.endpoint}"
            if self.app.debug and self.app.is_local_domain
            else f"{url_schema}://{self.app.domain}"
        )
        return f"{base_url}/{bucket}/{object_path.removeprefix('/')}"

    def get_url(self, path: str) -> str:
        return f"{self.base_url}/{path.removeprefix('/')}"


settings = Settings()
