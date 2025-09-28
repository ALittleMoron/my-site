import html
from collections.abc import Sequence
from dataclasses import dataclass, field

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token
from markdown_it.utils import EnvType, OptionsDict
from mdit_py_plugins import attrs, deflist, footnote, front_matter, tasklists

from config.constants import constants
from config.loggers import logger
from core.markdown.services import MarkdownService


class BootstrapRenderer(RendererHTML):
    __output__ = "html"

    def __init__(self, original_renderer: RendererHTML) -> None:
        self.original_renderer = original_renderer
        self.open_token_mapping = {
            "paragraph_open": constants.markdown_it.styles.paragraph_classes,
            "bullet_list_open": constants.markdown_it.styles.bullet_list_classes,
            "ordered_list_open": constants.markdown_it.styles.ordered_list_classes,
            "list_item_open": constants.markdown_it.styles.list_item_classes,
            "blockquote_open": constants.markdown_it.styles.blockquote_classes,
            "thead_open": constants.markdown_it.styles.thead_classes,
            "link_open": constants.markdown_it.styles.link_classes,
            "strong_open": constants.markdown_it.styles.strong_classes,
            "em_open": constants.markdown_it.styles.em_classes,
        }
        self.other_token_mapping = {
            "code_inline": constants.markdown_it.styles.code_inline_classes,
            "code_block": constants.markdown_it.styles.code_block_classes,
        }
        self.heading_stack: list[str] = []
        self._setup_custom_rules()

    def render(
        self,
        tokens: Sequence[Token],
        options: OptionsDict,
        env: EnvType,
    ) -> str:
        self._process_tokens(tokens)
        return self.original_renderer.render(tokens, options, env)

    def _setup_custom_rules(self) -> None:
        def fence_renderer(
            tokens: Sequence[Token],
            idx: int,
            _: OptionsDict,
            __: EnvType,
        ) -> str:
            token = tokens[idx]
            info = token.info.strip()
            lang = info.split()[0] if info else ""
            code_cls = f' class="language-{lang}"' if lang else ""
            return (
                f'<pre class="{constants.markdown_it.styles.code_block_classes}">'
                f"<code{code_cls}>{html.escape(token.content)}</code>"
                f"</pre>\n"
            )

        render_token = self.original_renderer.renderToken

        def table_open(
            tokens: Sequence[Token],
            idx: int,
            options: OptionsDict,
            env: EnvType,
        ) -> str:
            open_html = render_token(tokens, idx, options, env)
            return f'<div class="table-responsive">{open_html}'

        def table_close(
            tokens: Sequence[Token],
            idx: int,
            options: OptionsDict,
            env: EnvType,
        ) -> str:
            close_html = render_token(tokens, idx, options, env)
            return f"{close_html}</div>"

        self.original_renderer.rules["fence"] = fence_renderer  # type: ignore[assignment]
        self.original_renderer.rules["table_open"] = table_open  # type: ignore[assignment]
        self.original_renderer.rules["table_close"] = table_close  # type: ignore[assignment]

    def _process_tokens(self, tokens: Sequence[Token]) -> None:
        for token in tokens:
            if token.type.endswith("_open"):
                self._process_open_token(token)
            elif token.type.endswith("_close"):
                self._process_close_token(token)
            else:
                self._process_other_token(token)
            if token.children:
                self._process_tokens(token.children)

    def _process_open_token(self, token: Token) -> None:
        if token.type == "heading_open":
            return self._process_heading_open(token)
        if token.type == "table_open":
            return self._process_table_open(token)
        if token.type == "link_open":
            return self._process_link_open(token)
        if token.type == "bullet_list_open":
            return self._process_bullet_list_open(token)
        if token.type in self.open_token_mapping:
            return self._merge_class(token, self.open_token_mapping[token.type])
        return None

    def _process_close_token(self, token: Token) -> None:
        if token.type == "heading_close":
            return self._process_heading_close(token)
        if token.type == "table_close":
            return self._process_table_close(token)
        return None

    def _process_other_token(self, token: Token) -> None:
        if token.type == "image":
            self._merge_class(token, "img-fluid")
            if not token.attrGet("loading"):
                token.attrSet("loading", "lazy")
            if not token.attrGet("decoding"):
                token.attrSet("decoding", "async")
            return
        if token.type in self.other_token_mapping:
            self._merge_class(token, self.other_token_mapping[token.type])

    def _process_heading_open(self, token: Token) -> None:
        level = int(token.tag[1])
        if level not in constants.markdown_it.styles.heading_mapping:
            return
        new_tag, classes = constants.markdown_it.styles.heading_mapping[level]
        token.tag = new_tag
        self._merge_class(token, classes)
        self.heading_stack.append(new_tag)

    def _process_heading_close(self, token: Token) -> None:
        if self.heading_stack:
            token.tag = self.heading_stack.pop()

    def _process_table_open(self, token: Token) -> None:
        self._merge_class(token, constants.markdown_it.styles.table_classes)

    def _process_table_close(self, token: Token) -> None:
        pass

    def _process_bullet_list_open(self, token: Token) -> None:
        has_tasks = False
        for child in token.children or []:
            for grandchild in child.children or []:
                if grandchild.type == "paragraph_open":
                    for text_token in grandchild.children or []:
                        if text_token.type == "text" and text_token.content.strip().startswith(
                            ("[x]", "[ ]"),
                        ):
                            has_tasks = True
                            break
                if has_tasks:
                    break
            if has_tasks:
                break

        if has_tasks:
            return self._merge_class(token, "contains-task-list list-unstyled mb-3")
        return self._merge_class(token, constants.markdown_it.styles.bullet_list_classes)

    def _process_link_open(self, token: Token) -> None:
        self._merge_class(token, constants.markdown_it.styles.link_classes)
        href = token.attrGet("href") or ""
        if not isinstance(href, str):
            return
        if not href.startswith(("http://", "https://")) or token.attrGet("target"):
            return
        token.attrSet("target", "_blank")
        rel = token.attrGet("rel") or ""
        if not isinstance(rel, str) or ("noopener" in rel and "noreferrer" in rel):
            return
        parts = set(filter(None, rel.split()))
        parts.update({"noopener", "noreferrer"})
        token.attrSet("rel", " ".join(sorted(parts)))

    def _merge_class(self, token: Token, new_classes: str) -> None:
        token.attrJoin("class", new_classes)
        cls = token.attrGet("class")
        if not isinstance(cls, str) or not cls:
            return
        uniq = " ".join(dict.fromkeys(cls.split()))
        if uniq != cls:
            token.attrSet("class", uniq)


@dataclass(kw_only=True)
class MarkdownItService(MarkdownService):
    _md: MarkdownIt = field(init=False)

    def __post_init__(self) -> None:
        md = (
            MarkdownIt(
                "commonmark",
                {"html": True, "linkify": True, "typographer": True},
                renderer_cls=RendererHTML,
            )
            .use(attrs.attrs_plugin)
            .use(deflist.deflist_plugin)
            .use(footnote.footnote_plugin)
            .use(front_matter.front_matter_plugin)
            .use(tasklists.tasklists_plugin, enabled=True)
            .enable(["table", "strikethrough"])
        )
        md.renderer = BootstrapRenderer(md.renderer)  # type: ignore[arg-type]
        self._md = md

    def to_html(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        try:
            result = self._md.render(text)
        except (KeyError, TypeError, ValueError):
            logger.exception("MarkdownIt error")
            return '<p class="text-danger">Ошибка обработки markdown</p>'
        else:
            return str(result) if not isinstance(result, str) else result
