from services.markdown import MarkdownItService


def short_string(value: str, length: int = 50) -> str:
    return value[:length] + "..." if value and len(value) > length else value


def markdown_to_html(text: str) -> str:
    if not text:
        return ""
    return MarkdownItService().to_html(text)
