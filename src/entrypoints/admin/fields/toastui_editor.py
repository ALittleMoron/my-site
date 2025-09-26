from typing import Any

from jinja2 import Environment, BaseLoader
from markupsafe import Markup
from wtforms.fields import TextAreaField
from wtforms.widgets import html_params

from config.constants import constants


class ToastUIEditorWidget:
    validation_attrs: set[str] = {
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
    }

    def __call__(self, field: "ToastUIEditorField", **kwargs: Any) -> Markup:
        flags = getattr(field, "flags", {})
        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)
        attrs = {k: v for k, v in kwargs.items() if k in self.validation_attrs}
        editor_template = constants.path.template_dir / "sqladmin" / "_toastui_editor.html"
        return Markup(
            Environment(loader=BaseLoader())
            .from_string(editor_template.read_text())
            .render(
                textarea_id=field.id,
                textarea_name=field.name,
                attrs=html_params(**attrs),
                class_=kwargs.get("class", ""),
                initial_value=field._value(),
                edit_type="markdown",
                height="auto",
            )
        )


class ToastUIEditorField(TextAreaField):
    widget = ToastUIEditorWidget()
