from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True, frozen=True)
class _DirConstants:
    src_path: Path = Path(__file__).resolve().parent.parent
    root_path: Path = src_path.parent


@dataclass(kw_only=True, frozen=True)
class _MinioBucketNamesConstants:
    static: str = "static"
    media: str = "media"
