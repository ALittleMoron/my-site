from typing import Literal

from litestar.config.response_cache import CACHE_FOREVER
from pydantic import PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.files.types import Namespace
from core.i18n.enums import LanguageEnum
from core.schemas import Secret
from infra.config.constants import constants


class SecretStrExtended(SecretStr):
    def to_domain_secret(self) -> Secret[str]:
        return Secret(self.get_secret_value())


class _ProjectBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=constants.path.env_file, extra="ignore")


class _AppSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    url_schema: Literal["http", "https"]
    debug: bool
    secret_key: SecretStrExtended
    domain: str
    use_cache: bool
    contact_requests_enabled: bool

    @property
    def is_local_domain(self) -> bool:
        return self.domain in {"localhost", "127.0.0.1", "0.0.0.0"}  # noqa: S104  # nosec B104

    def get_cache_duration(
        self,
        value: bool | int | type[CACHE_FOREVER],  # noqa: FBT001
    ) -> bool | int | type[CACHE_FOREVER]:
        if self.use_cache:
            return value
        return 0


class _AdminSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="ADMIN_")

    init_login: str
    init_password: SecretStrExtended


class _DatabaseSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    user: str
    password: SecretStrExtended
    driver: str
    host: str
    port: str
    name: str
    pool_pre_ping: bool
    pool_size: int
    max_overflow: int
    expire_on_commit: bool
    log_query_metrics: bool
    slow_query_log_threshold_ms: int
    slow_query_log_statement_max_length: int

    @property
    def url(self) -> SecretStrExtended:
        return SecretStrExtended(
            f"{self.driver}://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}",
        )


class _AuthSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_")

    public_key: SecretStrExtended
    private_key: SecretStrExtended
    token_expire_seconds: int
    token_header_name: str
    token_prefix: str


class _MinioSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="MINIO_")

    host: str
    port: int
    secret_key: SecretStrExtended
    access_key: str
    secure: bool
    presign_put_expires_seconds: int

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"


class _SentrySettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="SENTRY_")

    use: bool
    dsn: str


class _ValkeySettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="VALKEY_")

    host: str
    port: int

    def get_url(self, db: int | str) -> SecretStrExtended:
        return SecretStrExtended(f"valkey://{self.host}:{self.port}/{db}")

    @property
    def url_for_http_cache(self) -> SecretStrExtended:
        return self.get_url(db=constants.valkey.databases.response_cache)


class _I18nSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="I18N_")

    default_language: LanguageEnum


class _CompetencyMatrixSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="COMPETENCY_MATRIX_")

    question_suggestion_anonymous_daily_limit: PositiveInt


class Settings:
    app: _AppSettings
    admin: _AdminSettings
    auth: _AuthSettings
    competency_matrix: _CompetencyMatrixSettings
    database: _DatabaseSettings
    i18n: _I18nSettings
    minio: _MinioSettings
    sentry: _SentrySettings
    valkey: _ValkeySettings

    def __init__(self) -> None:
        self.app = _AppSettings()
        self.admin = _AdminSettings()
        self.auth = _AuthSettings()
        self.competency_matrix = _CompetencyMatrixSettings()
        self.database = _DatabaseSettings()
        self.i18n = _I18nSettings()
        self.minio = _MinioSettings()
        self.sentry = _SentrySettings()
        self.valkey = _ValkeySettings()

    @property
    def base_url(self) -> str:
        postfix = ":8000" if self.app.debug and self.app.is_local_domain else ""
        return f"{self.app.url_schema}://{self.app.domain}{postfix}"

    def get_minio_object_url(self, object_path: str, bucket: Namespace) -> str:
        base_url = (
            f"{self.app.url_schema}://{self.minio.endpoint}"
            if self.app.debug and self.app.is_local_domain
            else f"{self.app.url_schema}://s3.{self.app.domain}"
        )
        return f"{base_url}/{bucket}/{object_path.removeprefix('/')}"

    def get_url(self, path: str) -> str:
        return f"{self.base_url}/{path.removeprefix('/')}"


settings = Settings()
