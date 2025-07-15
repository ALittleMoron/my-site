import uuid

from dishka import Provider, Scope, provide


class MockGeneralProvider(Provider):
    def __init__(self, uuid_: uuid.UUID | None = None):
        super().__init__()
        self.uuid_ = uuid_ or uuid.uuid4()
        print()

    @provide(scope=Scope.APP)
    async def provide_random_uuid(self) -> uuid.UUID:
        return self.uuid_
