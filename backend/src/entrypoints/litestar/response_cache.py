from collections.abc import Mapping
from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum
from typing import Any

from litestar import Request
from litestar.config.response_cache import default_cache_key_builder
from litestar.exceptions import ImproperlyConfiguredException
from litestar.stores.base import Store
from litestar.types.callable_types import CacheKeyBuilder

from infra.config.constants import constants
from infra.config.settings import settings


class ResponseCacheDomain(StrEnum):
    HEALTHCHECK = "healthcheck"
    I18N = "i18n"
    NOTES = "notes"
    COMPETENCY_MATRIX = "competency_matrix"

    @property
    def cache_key_builder(self) -> CacheKeyBuilder:
        def cache_key_builder(request: Request[Any, Any, Any]) -> str:
            separator = constants.response_cache.domain_key_separator
            return f"{self.value}{separator}{default_cache_key_builder(request)}"

        return cache_key_builder


@dataclass(kw_only=True, slots=True, frozen=True)
class ResponseCacheDomainStore(Store):
    stores: Mapping[ResponseCacheDomain, Store]

    async def set(
        self,
        key: str,
        value: str | bytes,
        expires_in: int | timedelta | None = None,
    ) -> None:
        store, store_key = self._get_domain_store(key=key)
        await store.set(key=store_key, value=value, expires_in=expires_in)

    async def get(self, key: str, renew_for: int | timedelta | None = None) -> bytes | None:
        store, store_key = self._get_domain_store(key=key)
        return await store.get(key=store_key, renew_for=renew_for)

    async def delete(self, key: str) -> None:
        store, store_key = self._get_domain_store(key=key)
        await store.delete(key=store_key)

    async def delete_all(self) -> None:
        for store in self.stores.values():
            await store.delete_all()

    async def delete_domain(self, domain: ResponseCacheDomain) -> None:
        await self.stores[domain].delete_all()

    async def exists(self, key: str) -> bool:
        store, store_key = self._get_domain_store(key=key)
        return await store.exists(key=store_key)

    async def expires_in(self, key: str) -> int | None:
        store, store_key = self._get_domain_store(key=key)
        return await store.expires_in(key=store_key)

    def _get_domain_store(self, *, key: str) -> tuple[Store, str]:
        domain_value, separator, store_key = key.partition(
            constants.response_cache.domain_key_separator,
        )
        if not separator or not store_key:
            msg = "Response cache key must start with a cache domain prefix."
            raise ImproperlyConfiguredException(msg)
        try:
            domain = ResponseCacheDomain(domain_value)
        except ValueError as exc:
            msg = f"Unknown response cache domain: {domain_value}"
            raise ImproperlyConfiguredException(msg) from exc
        return self.stores[domain], store_key


async def invalidate_response_cache_domain(
    *,
    request: Request[Any, Any, Any],
    domain: ResponseCacheDomain,
) -> None:
    if not settings.app.use_cache:
        return
    store = request.app.response_cache_config.get_store_from_app(request.app)
    if not isinstance(store, ResponseCacheDomainStore):
        msg = "Response cache store must be domain-routed."
        raise ImproperlyConfiguredException(msg)
    await store.delete_domain(domain=domain)
