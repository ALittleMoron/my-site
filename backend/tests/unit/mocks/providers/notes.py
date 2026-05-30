from unittest.mock import Mock

from dishka import Provider, Scope, provide

from core.notes.schemas import NotePublicStatsCollection
from core.notes.use_cases import AbstractNoteAnalyticsUseCase, AbstractNotesUseCase


class MockNotesProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_notes_use_case(self) -> AbstractNotesUseCase:
        return Mock(spec=AbstractNotesUseCase)

    @provide(scope=Scope.APP)
    async def provide_note_analytics_use_case(self) -> AbstractNoteAnalyticsUseCase:
        mock = Mock(spec=AbstractNoteAnalyticsUseCase)
        mock.get_public_stats.return_value = NotePublicStatsCollection(values=[])
        return mock
