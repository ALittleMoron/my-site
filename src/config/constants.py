from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass(kw_only=True, frozen=True)
class _PathConstants:
    src_dir: Path = Path(__file__).resolve().parent.parent
    root_dir: Path = src_dir.parent
    env_file: Path = root_dir / ".env"
    alembic_dir: Path = src_dir / "db" / "alembic"
    static_dir: Path = src_dir / "static"
    template_dir: Path = src_dir / "templates"


@dataclass(kw_only=True, frozen=True)
class _MinioBucketNamesConstants:
    static: Literal["static"] = "static"
    media: Literal["media"] = "media"


@dataclass(kw_only=True, frozen=True)
class _StaticFilesConstants:
    logo_dark = "core/icon-dark.png"
    logo_light = "core/icon-light.png"
    favicon = "favicon.ico"


@dataclass(kw_only=True, frozen=True)
class _ValkeyDatabaseConstants:
    response_cache: int = 0


@dataclass(kw_only=True, frozen=True)
class _ValkeyNamespaceConstants:
    framework: str = "LITESTAR"


@dataclass(kw_only=True, frozen=True)
class _ValkeyConstants:
    databases: _ValkeyDatabaseConstants = field(
        default_factory=lambda: _ValkeyDatabaseConstants(),
    )
    namespaces: _ValkeyNamespaceConstants = field(
        default_factory=lambda: _ValkeyNamespaceConstants(),
    )


class Constants:
    path: _PathConstants = _PathConstants()
    minio_buckets: _MinioBucketNamesConstants = _MinioBucketNamesConstants()
    static_files: _StaticFilesConstants = _StaticFilesConstants()
    valkey: _ValkeyConstants = _ValkeyConstants()


constants = Constants()
