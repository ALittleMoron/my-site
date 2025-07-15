import uuid

from dishka import Provider, Scope, provide


class GeneralProvider(Provider):
    @provide(scope=Scope.REQUEST, cache=False)
    async def provide_random_uuid(self) -> uuid.UUID:
        return uuid.uuid4()
