from pathlib import Path
from typing import Literal


class _PathConstants:
    src_dir: Path = Path(__file__).resolve().parent.parent.parent
    root_dir: Path = src_dir.parent
    backend_env_file: Path = root_dir / ".env"
    repository_env_file: Path = root_dir.parent / ".env"
    env_file: Path = backend_env_file if backend_env_file.exists() else repository_env_file
    infra_dir: Path = src_dir / "infra"
    alembic_dir: Path = infra_dir / "postgresql" / "alembic"


class _MinioBucketNamesConstants:
    media: Literal["media"] = "media"


class _ValkeyDatabaseConstants:
    response_cache: int = 0
    auth_revocations: int = 1


class _ValkeyNamespaceConstants:
    auth_revocations: str = "AUTH_REVOCATIONS"
    framework: str = "LITESTAR"


class _ValkeyConstants:
    databases: _ValkeyDatabaseConstants = _ValkeyDatabaseConstants()
    namespaces: _ValkeyNamespaceConstants = _ValkeyNamespaceConstants()


class _FilesConstants:
    allowed_to_upload_media_types: set[str] = {"image/png", "image/jpeg", "image/webp", "image/gif"}


class _SearchConstants:
    min_trigram_fuzzy_query_length: int = 6


class Constants:
    path: _PathConstants = _PathConstants()
    minio_buckets: _MinioBucketNamesConstants = _MinioBucketNamesConstants()
    valkey: _ValkeyConstants = _ValkeyConstants()
    files: _FilesConstants = _FilesConstants()
    search: _SearchConstants = _SearchConstants()


constants = Constants()
