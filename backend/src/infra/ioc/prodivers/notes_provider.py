from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.notes.event_dispatchers import NoteAnalyticsErrorReporter
from core.notes.storages import NoteAnalyticsStorage, NotesStorage
from core.notes.use_cases import (
    AbstractNoteAnalyticsUseCase,
    AbstractNotesUseCase,
    NoteAnalyticsUseCase,
    NotesUseCase,
)
from infra.config.settings import settings
from infra.notes.event_dispatchers import StructlogNoteAnalyticsErrorReporter
from infra.postgresql.storages.notes import NoteAnalyticsDatabaseStorage, NotesDatabaseStorage


class NotesProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_notes_storage(
        self,
        session: AsyncSession,
    ) -> NotesStorage:
        return NotesDatabaseStorage(session=session)

    @provide(scope=Scope.REQUEST)
    async def provide_note_analytics_storage(
        self,
        session: AsyncSession,
    ) -> NoteAnalyticsStorage:
        return NoteAnalyticsDatabaseStorage(session=session)

    @provide(scope=Scope.APP)
    async def provide_note_analytics_error_reporter(self) -> NoteAnalyticsErrorReporter:
        return StructlogNoteAnalyticsErrorReporter()

    @provide(scope=Scope.REQUEST)
    async def provide_notes_use_case(
        self,
        storage: NotesStorage,
    ) -> AbstractNotesUseCase:
        return NotesUseCase(storage=storage)

    @provide(scope=Scope.REQUEST)
    async def provide_note_analytics_use_case(
        self,
        storage: NotesStorage,
        analytics_storage: NoteAnalyticsStorage,
        error_reporter: NoteAnalyticsErrorReporter,
    ) -> AbstractNoteAnalyticsUseCase:
        return NoteAnalyticsUseCase(
            notes_storage=storage,
            analytics_storage=analytics_storage,
            reaction_secret=settings.app.secret_key.to_domain_secret(),
            app_domain=settings.app.domain,
            error_reporter=error_reporter,
        )
