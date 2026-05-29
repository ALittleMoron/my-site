from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.notes.storages import NotesStorage
from core.notes.use_cases import AbstractNotesUseCase, NotesUseCase
from infra.postgresql.storages.notes import NotesDatabaseStorage


class NotesProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_notes_storage(
        self,
        session: AsyncSession,
    ) -> NotesStorage:
        return NotesDatabaseStorage(session=session)

    @provide(scope=Scope.REQUEST)
    async def provide_notes_use_case(
        self,
        storage: NotesStorage,
    ) -> AbstractNotesUseCase:
        return NotesUseCase(storage=storage)
