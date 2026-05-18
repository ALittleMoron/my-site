from core.exceptions import EntryNotFoundError


class BlogPostNotFoundError(EntryNotFoundError):
    message = "Blog post not found"
