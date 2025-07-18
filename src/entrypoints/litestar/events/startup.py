import asyncio

from config.loggers import logger


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


def on_startup() -> None:
    loop = asyncio.get_running_loop()
    loop.create_task(monitor_event_loop_lag(loop))
