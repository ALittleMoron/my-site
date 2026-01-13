from collections.abc import Mapping
from typing import Any

from litestar.contrib.jinja import JinjaTemplateEngine

from config.constants import constants
from config.settings import settings
from services.markdown import MarkdownItService


def get_static_file_url(ctx: Mapping[str, Any], file_path: str) -> str:  # noqa: ARG001
    return settings.get_minio_object_url(bucket="static", object_path=file_path)


def markdown_to_html(ctx: Mapping[str, Any], text: str) -> str:  # noqa: ARG001
    if not text:
        return ""
    return MarkdownItService().to_html(text)


def register_template_callables(engine: JinjaTemplateEngine) -> None:
    engine.register_template_callable(
        key="get_static_file_url",
        template_callable=get_static_file_url,
    )
    engine.register_template_callable(
        key="get_full_url",
        template_callable=lambda ctx, path: settings.get_url(path=path),  # noqa: ARG005
    )
    engine.register_template_callable(
        key="markdown_to_html",
        template_callable=markdown_to_html,
    )
    engine.register_template_callable(
        key="get_settings",
        template_callable=lambda ctx: settings,  # noqa: ARG005
    )
    engine.register_template_callable(
        key="get_constants",
        template_callable=lambda ctx: constants,  # noqa: ARG005
    )
