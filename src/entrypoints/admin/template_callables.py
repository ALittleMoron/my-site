from services.markdown import MarkdownItService


def markdown_to_html(text: str) -> str:
    if not text:
        return ""
    return MarkdownItService().to_html(text)
