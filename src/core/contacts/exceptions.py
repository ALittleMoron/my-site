from core.exceptions import EntryNotFoundError


class ContactMePurchaseNotFoundError(EntryNotFoundError):
    message = "Contact me purchase not found"
