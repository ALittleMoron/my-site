import pytest

from services.markdown import MarkdownItService


class TestMarkdownItService:
    @pytest.fixture
    def markdown_service(self) -> MarkdownItService:
        return MarkdownItService()

    def test_to_html_basic_markdown(self, markdown_service: MarkdownItService) -> None:
        markdown_text = "# Заголовок\n\nЭто **жирный** текст и *курсив*."
        result = markdown_service.to_html(markdown_text)
        assert '<h3 class="fw-semibold mb-3">Заголовок</h3>' in result
        assert '<strong class="fw-bold">жирный</strong>' in result
        assert '<em class="fst-italic">курсив</em>' in result

    def test_to_html_empty_text(self, markdown_service: MarkdownItService) -> None:
        result = markdown_service.to_html("")
        assert result == ""

        result = markdown_service.to_html("   ")
        assert result == ""

    def test_to_html_none_text(self, markdown_service: MarkdownItService) -> None:
        result = markdown_service.to_html(None)  # type: ignore[arg-type]
        assert result == ""

    def test_to_html_tables(self, markdown_service: MarkdownItService) -> None:
        markdown_text = """
| Заголовок 1 | Заголовок 2 |
|-------------|-------------|
| Ячейка 1    | Ячейка 2    |
"""
        result = markdown_service.to_html(markdown_text)
        assert "table table-striped table-hover table-bordered" in result
        assert "table-dark" in result
        assert "<th>Заголовок 1</th>" in result
        assert "<td>Ячейка 1</td>" in result

    def test_to_html_strikethrough(self, markdown_service: MarkdownItService) -> None:
        markdown_text = "Это ~~зачеркнутый~~ текст."
        result = markdown_service.to_html(markdown_text)
        assert "<s>зачеркнутый</s>" in result

    def test_to_html_links(self, markdown_service: MarkdownItService) -> None:
        markdown_text = "Ссылка: https://example.com"
        result = markdown_service.to_html(markdown_text)
        assert "https://example.com" in result


class TestMarkdownTemplateCallable:
    def test_markdown_to_html_basic(self) -> None:
        from entrypoints.litestar.template_callables import markdown_to_html

        result = markdown_to_html(
            ctx={},
            text="# Test\n\nThis is **bold** text.",
        )

        assert '<h3 class="fw-semibold mb-3">Test</h3>' in result
        assert '<strong class="fw-bold">bold</strong>' in result

    def test_markdown_to_html_empty_text(self) -> None:
        from entrypoints.litestar.template_callables import markdown_to_html

        result = markdown_to_html(
            ctx={},
            text="",
        )

        assert result == ""

    def test_markdown_to_html_none_text(self) -> None:
        from entrypoints.litestar.template_callables import markdown_to_html

        result = markdown_to_html(
            ctx={},
            text="",  # Пустая строка вместо None
        )

        assert result == ""

    def test_markdown_to_html_none_text_actual(self) -> None:
        from entrypoints.litestar.template_callables import markdown_to_html

        # Тестируем реальное поведение с None
        result = markdown_to_html(
            ctx={},
            text=None,  # type: ignore[arg-type]
        )

        assert result == ""
