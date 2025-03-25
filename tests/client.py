import asyncio
from collections.abc import Coroutine
from inspect import iscoroutine
from typing import Any, Callable
from unittest.mock import Mock

from ninja.testing.client import NinjaClientBase, NinjaResponse


class SyncAndAsyncNinjaClient(NinjaClientBase):
    def _call(self, func: Callable | Coroutine, request: Mock, kwargs: dict[str, Any]) -> "NinjaResponse":
        response = func(request, **kwargs)
        if iscoroutine(response):
            return NinjaResponse(asyncio.run(response))
        return NinjaResponse(response)
