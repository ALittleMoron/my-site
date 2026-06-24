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

    @property
    def base_url(self) -> str:
        postfix = ":8000" if self.debug and self.is_local_domain else ""
        return f"{self.url_schema}://{self.domain}{postfix}"

    @property
    def public_origin(self) -> str:
        return f"{self.url_schema}://{self.domain}"

    def get_url(self, path: str) -> str:
        return f"{self.base_url}/{path.removeprefix('/')}"

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
    region: str
    secret_key: SecretStrExtended
    access_key: str
    secure: bool
    public_url: str
    presign_put_expires_seconds: int

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def internal_endpoint_url(self) -> str:
        schema = "https" if self.secure else "http"
        return f"{schema}://{self.endpoint}"

    @property
    def public_endpoint_url(self) -> str:
        return self.public_url.rstrip("/")

    def get_object_url(self, object_path: str, bucket: Namespace) -> str:
        return f"{self.public_endpoint_url}/{bucket}/{object_path.removeprefix('/')}"


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


class _TaskiqSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="TASKIQ_")

    cache_warm_interval_seconds: PositiveInt
    result_expire_seconds: PositiveInt


class _CacheWarmSettings(_ProjectBaseSettings):
    model_config = SettingsConfigDict(env_prefix="CACHE_WARM_")

    articles_page_size: PositiveInt


class Settings:
    app: _AppSettings
    admin: _AdminSettings
    auth: _AuthSettings
    cache_warm: _CacheWarmSettings
    competency_matrix: _CompetencyMatrixSettings
    database: _DatabaseSettings
    i18n: _I18nSettings
    minio: _MinioSettings
    sentry: _SentrySettings
    taskiq: _TaskiqSettings
    valkey: _ValkeySettings

    def __init__(self) -> None:
        self.app = _AppSettings()
        self.admin = _AdminSettings()
        self.auth = _AuthSettings()
        self.cache_warm = _CacheWarmSettings()
        self.competency_matrix = _CompetencyMatrixSettings()
        self.database = _DatabaseSettings()
        self.i18n = _I18nSettings()
        self.minio = _MinioSettings()
        self.sentry = _SentrySettings()
        self.taskiq = _TaskiqSettings()
        self.valkey = _ValkeySettings()


settings = Settings()
