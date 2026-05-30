from abc import ABC, abstractmethod

from core.notes.schemas import Note


class NoteAnalyticsErrorReporter(ABC):
    @abstractmethod
    def report_public_view_tracking_failure(self, *, note: Note, error: Exception) -> None:
        raise NotImplementedError
