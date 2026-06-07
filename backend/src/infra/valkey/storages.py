import hashlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from litestar.stores.base import Store
from valkey.asyncio import Valkey

from core.auth.storages import TokenRevocationStorage
from core.auth.types import Token
from core.competency_matrix.schemas import QuestionSuggestionQuota
from core.competency_matrix.storages import QuestionSuggestionQuotaStorage

QuotaScript = Callable[..., Awaitable[int]]


@dataclass(kw_only=True, slots=True, frozen=True)
class ValkeyTokenRevocationStorage(TokenRevocationStorage):
    store: Store

    async def revoke_token(self, token: Token, expires_in_seconds: int) -> None:
        await self.store.set(
            key=self._token_key(token),
            value=b"revoked",
            expires_in=expires_in_seconds,
        )

    async def is_token_revoked(self, token: Token) -> bool:
        return await self.store.exists(key=self._token_key(token))

    def _token_key(self, token: Token) -> str:
        return hashlib.sha256(token).hexdigest()


@dataclass(kw_only=True, slots=True)
class ValkeyQuestionSuggestionQuotaStorage(QuestionSuggestionQuotaStorage):
    valkey: Valkey
    namespace: str
    _consume_quota_script: QuotaScript = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._consume_quota_script = self.valkey.register_script(
            b"""
            local value = redis.call('INCR', KEYS[1])
            if value == 1 then
                redis.call('EXPIRE', KEYS[1], tonumber(ARGV[1]))
            end
            return value
            """,
        )

    async def consume_question_suggestion_quota(
        self,
        *,
        actor_key: str,
        limit: int,
        ttl_seconds: int,
    ) -> QuestionSuggestionQuota:
        consumed = await self._consume_quota_script(
            keys=[self._quota_key(actor_key=actor_key)],
            args=[ttl_seconds],
        )
        return QuestionSuggestionQuota(
            allowed=consumed <= limit,
            remaining=max(limit - consumed, 0),
        )

    def _quota_key(self, *, actor_key: str) -> str:
        return f"{self.namespace}:{actor_key}"
