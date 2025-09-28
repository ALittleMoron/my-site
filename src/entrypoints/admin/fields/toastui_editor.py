from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from jinja2 import BaseLoader, Environment
from markupsafe import Markup
from wtforms.fields import TextAreaField
from wtforms.widgets import html_params

from config.constants import constants

toastui_editor_template: Path = constants.path.template_dir / "sqladmin" / "_toastui_editor.html"


@dataclass(kw_only=True)
class ToastUIEditorRenderParams:
    textarea_id: str
    textarea_name: str
    attrs: dict[str, Any]
    class_: str
    initial_value: str
    edit_type: Literal["markdown", "wysiwyg"]
    height: str


class ToastUIEditorWidget:
    validation_attrs: set[str] = {
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
    }

    def prepare_params(
        self,
        field: "ToastUIEditorField",
        kwargs: dict[str, Any],
    ) -> ToastUIEditorRenderParams:
        kwargs.update({k: v for k, v in vars(field.flags).items() if k in self.validation_attrs})
        attrs = {k: v for k, v in kwargs.items() if k in self.validation_attrs}
        return ToastUIEditorRenderParams(
            textarea_id=field.id,
            textarea_name=field.name,
            attrs=html_params(**attrs),
            class_=kwargs.pop("class", ""),
            initial_value=field._value(),  # noqa: SLF001
            edit_type="markdown",
            height="auto",
        )

    def __call__(self, field: "ToastUIEditorField", **kwargs: Any) -> Markup:  # noqa: ANN401
        return Markup(  # noqa: S704
            Environment(loader=BaseLoader(), autoescape=True)
            .from_string(toastui_editor_template.read_text())
            .render(params=self.prepare_params(field=field, kwargs=kwargs)),
        )


class ToastUIEditorField(TextAreaField):
    widget = ToastUIEditorWidget()
