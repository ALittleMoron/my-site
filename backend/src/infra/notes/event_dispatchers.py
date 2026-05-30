from dataclasses import dataclass

from core.notes.event_dispatchers import NoteAnalyticsErrorReporter
from core.notes.schemas import Note
from infra.config.loggers import logger


@dataclass(frozen=True, slots=True)
class StructlogNoteAnalyticsErrorReporter(NoteAnalyticsErrorReporter):
    def report_public_view_tracking_failure(self, *, note: Note, error: Exception) -> None:
        logger.exception(
            "Could not track public note view",
            note_id=str(note.id),
            note_slug=note.slug,
            exc_info=(type(error), error, error.__traceback__),
        )
