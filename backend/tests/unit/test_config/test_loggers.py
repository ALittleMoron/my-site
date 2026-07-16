import json

import ecs_logging
import structlog

from infra.config.loggers import (
    build_project_logging_config,
    configure_project_logging,
    log_sanitized_exception,
)


def test_project_logging_config_selects_debug_console_renderer() -> None:
    config = build_project_logging_config(debug=True)

    assert isinstance(config.processors[-1], structlog.dev.ConsoleRenderer)


def test_project_logging_config_selects_ecs_renderer() -> None:
    config = build_project_logging_config(debug=False)

    assert isinstance(config.processors[-1], ecs_logging.StructlogFormatter)


def test_sanitized_exception_log_excludes_exception_message() -> None:
    secret_marker = "AUTHORED_SECRET_MARKER_7d523e"  # noqa: S105
    configure_project_logging(debug=False)

    with structlog.testing.capture_logs() as logs:
        log_sanitized_exception(
            event="agent_request_failed",
            error=RuntimeError(secret_marker),
            request_id="request-id",
        )

    assert secret_marker not in json.dumps(logs)
    assert logs == [
        {
            "event": "agent_request_failed",
            "exception_type": "RuntimeError",
            "log_level": "error",
            "request_id": "request-id",
        },
    ]
