from core.exceptions import EntryNotFoundError


class UserNotFoundError(EntryNotFoundError):
    message = "User not found"
