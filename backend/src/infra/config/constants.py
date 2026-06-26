from pathlib import Path
from typing import Literal

from core.competency_matrix.schemas import QuestionQueueImportRules


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
    question_suggestion_quota: int = 2
    taskiq_broker: int = 3
    taskiq_results: int = 4


class _ValkeyNamespaceConstants:
    auth_revocations: str = "AUTH_REVOCATIONS"
    framework: str = "LITESTAR"
    matrix_question_suggestions: str = "MATRIX_QUESTION_SUGGESTIONS"


class _ValkeyConstants:
    databases: _ValkeyDatabaseConstants = _ValkeyDatabaseConstants()
    namespaces: _ValkeyNamespaceConstants = _ValkeyNamespaceConstants()


class _ResponseCacheConstants:
    store_name: Literal["litestar_cache"] = "litestar_cache"
    domain_key_separator: Literal[":"] = ":"
    default_ttl_seconds: int = 86_400
    json_content_type_header_name: bytes = b"content-type"
    json_content_type_header_value: bytes = b"application/json"


class _TaskiqConstants:
    queue_name: Literal["my_site_background"] = "my_site_background"
    consumer_group_name: Literal["my_site_background"] = "my_site_background"
    result_prefix: Literal["my_site_taskiq_results"] = "my_site_taskiq_results"
    cache_warm_all_task_name: Literal["cache_warm_all"] = "cache_warm_all"
    cache_warm_domain_task_name: Literal["cache_warm_domain"] = "cache_warm_domain"


class _FilesConstants:
    allowed_to_upload_media_types: set[str] = {"image/png", "image/jpeg", "image/webp", "image/gif"}


class _ResumeExportConstants:
    fonts_dir: Path = _PathConstants.infra_dir / "resume_export" / "fonts"
    font_regular_path: Path = fonts_dir / "NotoSans-Regular.ttf"
    font_bold_path: Path = fonts_dir / "NotoSans-Bold.ttf"
    font_license_path: Path = fonts_dir / "OFL.txt"
    font_regular_name: Literal["NotoSans"] = "NotoSans"
    font_bold_name: Literal["NotoSans-Bold"] = "NotoSans-Bold"
    content_disposition_header_name: Literal["Content-Disposition"] = "Content-Disposition"
    pdf_media_type: Literal["application/pdf"] = "application/pdf"
    docx_media_type: Literal[
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    pdf_extension: Literal["pdf"] = "pdf"
    docx_extension: Literal["docx"] = "docx"


class _SearchConstants:
    min_trigram_fuzzy_query_length: int = 6


class _QuestionQueueImportConstants:
    rules: QuestionQueueImportRules = QuestionQueueImportRules(
        supported_text_extensions=frozenset({".txt", ".csv"}),
        supported_excel_extensions=frozenset({".xlsx", ".xlsm"}),
        unsupported_legacy_excel_extensions=frozenset({".xls"}),
        supported_extensions_for_message=(".txt", ".csv", ".xlsx", ".xlsm"),
        question_headers=frozenset({"question", "questions", "вопрос", "вопросы"}),
        question_headers_for_message=("question", "questions", "вопрос", "вопросы"),
        csv_delimiters=",;\t|",
        question_max_length=255,
    )


class _AdminValidationConstants:
    slug_pattern: str = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    short_text_max_length: int = 255
    url_max_length: int = 2_048
    seo_description_max_length: int = 320
    email_max_length: int = 254
    article_content_max_length: int = 100_000
    matrix_long_text_max_length: int = 20_000
    resume_long_text_max_length: int = 10_000


class Constants:
    path: _PathConstants = _PathConstants()
    minio_buckets: _MinioBucketNamesConstants = _MinioBucketNamesConstants()
    valkey: _ValkeyConstants = _ValkeyConstants()
    response_cache: _ResponseCacheConstants = _ResponseCacheConstants()
    taskiq: _TaskiqConstants = _TaskiqConstants()
    files: _FilesConstants = _FilesConstants()
    resume_export: _ResumeExportConstants = _ResumeExportConstants()
    search: _SearchConstants = _SearchConstants()
    question_queue_import: _QuestionQueueImportConstants = _QuestionQueueImportConstants()
    admin_validation: _AdminValidationConstants = _AdminValidationConstants()


constants = Constants()
