from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.constants import _DirConstants, _MinioBucketNamesConstants, _StaticFilesConstants


class _AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    debug: bool = True
    secret_key: SecretStr = SecretStr("SECRET_KEY")
    domain_host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000


class _DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

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
            "{driver}://{user}:{password}@{host}:{port}/{name}".format(
                driver=self.driver,
                user=self.user,
                password=self.password.get_secret_value(),
                host=self.host,
                port=self.port,
                name=self.name,
            )
        )


class _AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ADMIN_")

    public_key_pem_file_name: str = "public.pem"
    secret_key_pem_file_name: str = "private.pem"
    token_expire_seconds: int = 60 * 60 * 24 * 2
    crypto_schemes: list[str] = ["bcrypt"]


class _MinioSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MINIO_")

    host: str = "localhost"
    port: int = 9000
    secret_key: SecretStr = SecretStr("")
    access_key: str = ""
    secure: bool = False
    bucket_names: _MinioBucketNamesConstants = _MinioBucketNamesConstants()
    static_files: _StaticFilesConstants = _StaticFilesConstants()

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"


class Settings(BaseSettings):
    app: _AppConfig = _AppConfig()
    auth: _AuthConfig = _AuthConfig()
    dir: _DirConstants = _DirConstants()
    database: _DatabaseConfig = _DatabaseConfig()
    minio: _MinioSettings = _MinioSettings()

    @property
    def minio_url(self) -> str:
        schema = "https" if self.minio.secure else "http"
        is_local_domain = self.app.domain_host in {'localhost', '127.0.0.1', '0.0.0.0'}
        port = f':{self.minio.port}' if is_local_domain else ""
        path = '' if is_local_domain else '/minio'
        return f'{schema}://{self.app.domain_host}{port}{path}'

    def get_minio_object_url(self, bucket: str, object_path: str) -> str:
        if object_path.startswith("/"):
            object_path = object_path[1:]
        return f"{self.minio_url}/{bucket}/{object_path}"


settings = Settings()
