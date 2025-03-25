from core.exceptions import EntryNotFoundError


class CompetencyMatrixItemNotFoundError(EntryNotFoundError):
    message = "Competency matrix item not found"
