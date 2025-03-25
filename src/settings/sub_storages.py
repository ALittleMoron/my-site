from settings.config import config

MINIO_POLICY_HOOKS: list[tuple[str, dict]] = []
MINIO_USE_HTTPS = config.minio.use_https
MINIO_ENDPOINT = config.minio.endpoint
MINIO_ACCESS_KEY = config.minio.access_key.get_secret_value()
MINIO_SECRET_KEY = config.minio.secret_key.get_secret_value()
MINIO_URL_EXPIRY_HOURS = config.minio.url_expiry_hours
MINIO_CONSISTENCY_CHECK_ON_START = config.minio.consistency_check_on_start
MINIO_BUCKET_CHECK_ON_SAVE = config.minio.bucket_check_on_save
MINIO_PUBLIC_BUCKETS = config.minio.public_buckets
MINIO_PRIVATE_BUCKETS = config.minio.private_buckets
MINIO_MEDIA_FILES_BUCKET = config.minio.media_files_bucket
MINIO_STATIC_FILES_BUCKET = config.minio.static_files_bucket
DEFAULT_FILE_STORAGE = "django_minio_backend.models.MinioBackend"
STATICFILES_STORAGE = "django_minio_backend.models.MinioBackendStatic"
STORAGES = {
    "default": {"BACKEND": "django_minio_backend.models.MinioBackend"},
    "staticfiles": {"BACKEND": "django_minio_backend.models.MinioBackendStatic"},
}
# TODO: FIXME
STATIC_URL = "http://localhost:9000/admin-static/"
MEDIA_URL = "http://localhost:9000/media/"
STATICFILES_DIRS = [config.dir.src_path / "static/"]
