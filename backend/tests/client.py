import asyncio
from collections.abc import Callable
from inspect import iscoroutine
from typing import Any
from unittest.mock import Mock

from ninja.testing.client import NinjaClientBase, NinjaResponse


class SyncAndAsyncNinjaClient(NinjaClientBase):
    def _call(
        self,
        func: Callable,
        request: Mock,
        kwargs: dict[str, Any],
    ) -> "NinjaResponse":
        response = func(request, **kwargs)
        if iscoroutine(response):
            return NinjaResponse(asyncio.run(response))
        return NinjaResponse(response)
