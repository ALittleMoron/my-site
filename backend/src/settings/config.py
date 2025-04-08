from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass(kw_only=True, frozen=True)
class _DirConstants:
    src_path: Path = Path(__file__).resolve().parent.parent
    root_path: Path = src_path.parent


class _CSRFConfig(BaseSettings):
    cookie_httponly: bool = False
    trusted_origins: list[str] = ["http://localhost:8000"]

    model_config = SettingsConfigDict(env_prefix="CSRF_")


class _AppConfig(BaseSettings):
    debug: bool = True
    secret_key: SecretStr = SecretStr("abc")
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8080
    x_frame_options: str = "SAMEORIGIN"
    internal_ips: list[str] = ["127.0.0.1"]
    language_code: str = "ru-Ru"
    time_zone: str = "Europe/Moscow"
    use_i18n: bool = True
    use_tz: bool = True

    model_config = SettingsConfigDict(env_prefix="APP_")


class _MinioConfig(BaseSettings):
    use_https: bool = False
    endpoint: str = "localhost:9000"
    access_key: SecretStr = SecretStr("minioadmin")
    secret_key: SecretStr = SecretStr("minioadmin")
    url_expiry_hours: timedelta = timedelta(days=1)
    consistency_check_on_start: bool = True
    bucket_check_on_save: bool = True
    public_buckets: list[str] = ["media", "admin-static"]
    private_buckets: list[str] = []
    media_files_bucket: str = "media"
    static_files_bucket: str = "admin-static"

    model_config = SettingsConfigDict(env_prefix="MINIO_")


class _DatabaseConfig(BaseSettings):
    user: str = "postgres"
    password: SecretStr = SecretStr("postgres")
    host: str = "localhost"
    port: str = "5432"
    name: str = "my_site_database"

    model_config = SettingsConfigDict(env_prefix="DB_")


class _MartorConfig(BaseSettings):
    enable_label: bool = True
    enable_admin_css: bool = False
    markdownify_timeout: int = 0
    upload_path: str = "martor"
    upload_url: str = "/markdown-upload-image"
    max_image_upload_size: int = 10485760

    model_config = SettingsConfigDict(env_prefix="MARTOR_")


class Config(BaseSettings):
    app: _AppConfig = _AppConfig()
    csrf: _CSRFConfig = _CSRFConfig()
    dir: _DirConstants = _DirConstants()
    minio: _MinioConfig = _MinioConfig()
    database: _DatabaseConfig = _DatabaseConfig()
    martor: _MartorConfig = _MartorConfig()


config = Config()
