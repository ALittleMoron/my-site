from core.exceptions import EntryNotFoundError


class ArticleNotFoundError(EntryNotFoundError):
    message = "Article not found"


class TagNotFoundError(EntryNotFoundError):
    message = "Tag not found"
