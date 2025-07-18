from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(kw_only=True, frozen=True)
class _DirConstants:
    src_path: Path = Path(__file__).resolve().parent.parent
    root_path: Path = src_path.parent
    certs_path: Path = root_path / "certs"
    alembic_path: Path = src_path / "db" / "alembic"


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
    dir: _DirConstants = _DirConstants()
    minio_buckets: _MinioBucketNamesConstants = _MinioBucketNamesConstants()
    static_files: _StaticFilesConstants = _StaticFilesConstants()


constants = Constants()
