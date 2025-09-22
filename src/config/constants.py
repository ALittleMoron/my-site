from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(kw_only=True, frozen=True)
class _PathConstants:
    src_dir: Path = Path(__file__).resolve().parent.parent
    root_dir: Path = src_dir.parent
    env_file: Path = root_dir / ".env"
    alembic_dir: Path = src_dir / "db" / "alembic"
    static_dir: Path = src_dir / "static"


@dataclass(kw_only=True, frozen=True)
class _MinioBucketNamesConstants:
    static: Literal["static"] = "static"
    media: Literal["media"] = "media"


@dataclass(kw_only=True, frozen=True)
class _StaticFilesConstants:
    logo_dark = "core/icon-dark.png"
    logo_light = "core/icon-light.png"
    favicon = "favicon.ico"


class Constants:
    path: _PathConstants = _PathConstants()
    minio_buckets: _MinioBucketNamesConstants = _MinioBucketNamesConstants()
    static_files: _StaticFilesConstants = _StaticFilesConstants()


constants = Constants()
