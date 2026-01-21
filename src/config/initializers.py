import asyncio

import pem
import sentry_sdk
from sentry_sdk.integrations.litestar import LitestarIntegration

from config.loggers import logger
from config.settings import settings
from db.utils import migrate


def init_sentry() -> None:
    if not settings.sentry.use:
        # NOTE: просто не надо во время локальной разработки срать в sentry. На проде можно
        #
        # debug использую, потому что у меня нет много окружений. Только прод и локальный запуск.
        # Поэтому мне не нужно на каждый инструмент делать параметр enabled.
        return
    sentry_sdk.init(
        dsn=settings.sentry.dsn,
        send_default_pii=True,
        traces_sample_rate=1.0,
        enable_logs=True,
        profile_lifecycle="trace",
        integrations=[LitestarIntegration()],
    )


def check_certs_exists() -> None:
    if not pem.parse(settings.auth.public_key.get_secret_value()):
        msg = "Public key certificate is not valid. Check your .env file or environment variables."
        raise RuntimeError(msg)
    if not pem.parse(settings.auth.private_key.get_secret_value()):
        msg = "Private key certificate is not valid. Check your .env file or environment variables."
        raise RuntimeError(msg)


async def monitor_event_loop_lag(loop: asyncio.AbstractEventLoop) -> None:
    start = loop.time()
    sleep_interval = 1

    while loop.is_running():
        await asyncio.sleep(sleep_interval)
        diff = loop.time() - start
        lag = diff - sleep_interval
        if lag > 1:
            coro_names = {
                task._coro.cr_code.co_qualname  # type: ignore[attr-defined]  # noqa: SLF001
                for task in asyncio.all_tasks(loop)
                if task._coro.cr_code.co_name != "monitor_event_loop_lag"  # type: ignore[attr-defined]  # noqa: SLF001
            }
            logger.warn("Event loop has lag", lag=lag, coroutine_names=coro_names)
        start = loop.time()


def before_app_create() -> None:
    loop = asyncio.get_running_loop()
    init_sentry()
    check_certs_exists()
    # TODO: move migrate to separated task in docker-compose
    migrate("head")
    loop.create_task(monitor_event_loop_lag(loop))  # noqa: RUF006
