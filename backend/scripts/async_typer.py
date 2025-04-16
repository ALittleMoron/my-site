from asyncio import run
from functools import wraps
from typing import TypeVar, ParamSpec, Any, Callable, Coroutine

import typer

T = TypeVar("T")
P = ParamSpec("P")


class AsyncTyper(typer.Typer):
    """Typer с асинхронным декоратором для объявления асинхронных команд."""

    def async_command(self: typer.Typer, *args: Any, **kwargs: Any):  # noqa: ANN201 ANN401
        """Декоратор для добавления синхронной версии команды в экземпляр Typer'а."""

        def decorator(
            async_func: Callable[P, Coroutine[None, None, T]],
        ) -> Callable[P, Coroutine[None, None, T]]:
            @wraps(async_func)
            def sync_func(*_args: P.args, **_kwargs: P.kwargs) -> T:
                return run(async_func(*_args, **_kwargs))

            self.command(*args, **kwargs)(sync_func)
            return async_func

        return decorator
