from core.exceptions import EntryNotFoundError


class NoteNotFoundError(EntryNotFoundError):
    message = "Note not found"


class TagNotFoundError(EntryNotFoundError):
    message = "Tag not found"
