import asyncio

import sentry_sdk
from sentry_sdk.integrations.litestar import LitestarIntegration

from config.constants import constants
from config.loggers import logger
from config.settings import settings
from db.utils import migrate


def init_sentry() -> None:
    if settings.app.debug:
        # NOTE: просто не надо во время локальной разработки срать в sentry. На проде можно
        #
        # debug использую, потому что у меня нет много окружений. Только прод и локальный запуск.
        # Поэтому мне не нужно на каждый инструмент делать параметр enabled.
        return
    sentry_sdk.init(
        dsn=settings.sentry.dsn,
        send_default_pii=True,
        integrations=[LitestarIntegration()],
    )


def check_certs_exists() -> None:
    if not (constants.dir.certs_path / "public.pem").exists():
        msg = "Public key certificate file does not exists."
        raise RuntimeError(msg)
    if not (constants.dir.certs_path / "private.pem").exists():
        msg = "Secret key certificate file does not exists."
        raise RuntimeError(msg)


async def monitor_event_loop_lag(loop: asyncio.AbstractEventLoop):
    start = loop.time()
    sleep_interval = 1

    while loop.is_running():
        await asyncio.sleep(sleep_interval)
        diff = loop.time() - start
        lag = diff - sleep_interval
        if lag > 1:
            coro_names = {
                task._coro.cr_code.co_qualname
                for task in asyncio.all_tasks(loop)
                if task._coro.cr_code.co_name != 'monitor_event_loop_lag'
            }
            logger.warn(f"Event loop has lag", lag=lag, coroutine_names=coro_names)
        start = loop.time()


def before_app_create() -> None:
    loop = asyncio.get_running_loop()
    check_certs_exists()
    migrate("head")
    loop.create_task(monitor_event_loop_lag(loop))
