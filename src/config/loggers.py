import logging
from collections.abc import Callable

import ecs_logging
import structlog
from structlog.typing import BindableLogger, Processor, WrappedLogger

from config.settings import settings

processors: list[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.UnicodeDecoder(),
    structlog.dev.set_exc_info,
    structlog.processors.StackInfoRenderer(),
]
wrapper_class: type[BindableLogger] = structlog.make_filtering_bound_logger(logging.NOTSET)
logger_factory: Callable[..., WrappedLogger] = structlog.PrintLoggerFactory()
cache_logger_on_first_use = True

if settings.app.debug:
    processors += [
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.dev.ConsoleRenderer(),
    ]
    wrapper_class = structlog.make_filtering_bound_logger(logging.DEBUG)
else:
    processors += [
        ecs_logging.StructlogFormatter(),  # type: ignore[list-item]
    ]
    wrapper_class = structlog.make_filtering_bound_logger(logging.INFO)

structlog.configure(
    processors=processors,
    wrapper_class=wrapper_class,
    logger_factory=logger_factory,
    cache_logger_on_first_use=cache_logger_on_first_use,
)
logger: structlog.stdlib.BoundLogger = structlog.get_logger()
