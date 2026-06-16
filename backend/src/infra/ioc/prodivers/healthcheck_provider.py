from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from miniopy_async.api import Minio
from sqlalchemy.ext.asyncio import AsyncSession
from valkey.asyncio import Valkey

from infra.config.constants import constants
from infra.config.settings import settings
from infra.healthcheck import ReadinessChecker


class HealthcheckProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_readiness_valkey(self) -> AsyncIterable[Valkey]:
        client = Valkey.from_url(
            settings.valkey.get_url(
                db=constants.valkey.databases.response_cache,
            ).get_secret_value(),
        )
        yield client
        await client.aclose()

    @provide(scope=Scope.REQUEST)
    async def provide_readiness_checker(
        self,
        session: AsyncSession,
        minio_client: Minio,
        readiness_valkey: Valkey,
    ) -> ReadinessChecker:
        return ReadinessChecker(
            session=session,
            valkey=readiness_valkey,
            minio_client=minio_client,
        )
