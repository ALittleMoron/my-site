from unittest.mock import Mock

from dishka import Provider, Scope, provide

from core.notes.use_cases import AbstractNotesUseCase


class MockNotesProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_notes_use_case(self) -> AbstractNotesUseCase:
        return Mock(spec=AbstractNotesUseCase)
