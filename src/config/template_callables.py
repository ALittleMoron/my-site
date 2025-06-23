from collections.abc import Mapping
from typing import Any

from litestar.contrib.jinja import JinjaTemplateEngine

from config.settings import settings


def get_static_file_url(ctx: Mapping[str, Any], file_path: str) -> str:  # noqa: ARG001
    return settings.get_minio_object_url(bucket="static", object_path=file_path)


def register_template_callables(engine: JinjaTemplateEngine) -> None:
    engine.register_template_callable(
        key="get_static_file_url",
        template_callable=get_static_file_url,
    )
