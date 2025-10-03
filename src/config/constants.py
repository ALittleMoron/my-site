from pathlib import Path
from typing import Literal


class _PathConstants:
    src_dir: Path = Path(__file__).resolve().parent.parent
    root_dir: Path = src_dir.parent
    env_file: Path = root_dir / ".env"
    alembic_dir: Path = src_dir / "db" / "alembic"
    static_dir: Path = src_dir / "static"
    template_dir: Path = src_dir / "templates"


class _MinioBucketNamesConstants:
    static: Literal["static"] = "static"
    media: Literal["media"] = "media"


class _StaticFilesConstants:
    logo_dark = "core/icon-dark.png"
    logo_light = "core/icon-light.png"
    favicon = "favicon.ico"


class _ValkeyDatabaseConstants:
    response_cache: int = 0


class _ValkeyNamespaceConstants:
    framework: str = "LITESTAR"


class _ValkeyConstants:
    databases: _ValkeyDatabaseConstants = _ValkeyDatabaseConstants()
    namespaces: _ValkeyNamespaceConstants = _ValkeyNamespaceConstants()


class _MarkdownStylesConstants:
    paragraph_classes: str = "text-secondary mb-3"
    bullet_list_classes: str = "list-unstyled mb-3"
    ordered_list_classes: str = "mb-3"
    list_item_classes: str = "mb-1 text-secondary"
    blockquote_classes: str = "blockquote border-start border-3 border-success ps-3"
    table_classes: str = "table table-striped table-hover table-bordered"
    thead_classes: str = "table-dark"
    code_inline_classes: str = ""
    code_block_classes: str = ""
    link_classes: str = "p-0 text-body-secondary link-active"
    strong_classes: str = "fw-bold"
    em_classes: str = "fst-italic"
    heading_mapping: dict[int, tuple[str, str]] = {
        1: ("h3", "fw-semibold mb-3"),
        2: ("h4", "fw-semibold mb-3"),
        3: ("h5", "fw-semibold mb-3"),
        4: ("h6", "fw-semibold mb-3"),
        5: ("h6", "fw-semibold mb-3"),
        6: ("h6", "fw-semibold mb-3"),
    }


class _MarkdownConstants:
    styles: _MarkdownStylesConstants = _MarkdownStylesConstants()


class _AdminConstants:
    allowed_media_types: set[str] = {"image/png", "image/jpeg", "image/webp", "image/gif"}


class Constants:
    path: _PathConstants = _PathConstants()
    minio_buckets: _MinioBucketNamesConstants = _MinioBucketNamesConstants()
    static_files: _StaticFilesConstants = _StaticFilesConstants()
    valkey: _ValkeyConstants = _ValkeyConstants()
    markdown_it: _MarkdownConstants = _MarkdownConstants()
    admin: _AdminConstants = _AdminConstants()


constants = Constants()
