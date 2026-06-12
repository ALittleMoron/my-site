from dataclasses import dataclass
from urllib.parse import urlencode

import msgspec
from pydantic import BaseModel

from entrypoints.litestar.response_cache import ResponseCacheDomainStore
from entrypoints.taskiq.cache_warm.targets import CacheWarmTarget
from infra.config.constants import constants


@dataclass(frozen=True, slots=True)
class ResponseCacheKeyBuilder:
    def build(self, *, target: CacheWarmTarget) -> str:
        query_string = urlencode(sorted(target.query), doseq=True)
        return (
            f"{target.domain.value}"
            f"{constants.response_cache.domain_key_separator}"
            f"GET{target.path}{query_string}"
        )


@dataclass(frozen=True, slots=True)
class ResponseCachePayloadCodec:
    def encode(self, *, response: BaseModel) -> bytes:
        messages = [
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (
                        constants.response_cache.json_content_type_header_name,
                        constants.response_cache.json_content_type_header_value,
                    ),
                ],
            },
            {
                "type": "http.response.body",
                "body": response.model_dump_json(by_alias=True).encode(),
            },
        ]
        return msgspec.msgpack.encode(messages)


@dataclass(frozen=True, slots=True)
class ResponseCacheWarmWriter:
    store: ResponseCacheDomainStore
    key_builder: ResponseCacheKeyBuilder
    payload_codec: ResponseCachePayloadCodec

    async def write_target(self, target: CacheWarmTarget) -> None:
        await self.store.set(
            key=self.key_builder.build(target=target),
            value=self.payload_codec.encode(response=target.response),
            expires_in=constants.response_cache.default_ttl_seconds,
        )
