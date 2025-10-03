from db.models import CompetencyMatrixItemModel, ExternalResourceModel
from entrypoints.admin.fields.toastui_editor import ToastUIEditorField
from entrypoints.admin.template_callables import markdown_to_html
from entrypoints.admin.views.base import (
    ModelViewWithDeleteAction,
    ModelViewWithPublishAction,
)


class ExternalResourceView(
    ModelViewWithDeleteAction,
    model=ExternalResourceModel,
):
    icon = "fa-solid fa-book-open"
    category_icon = "fa-thin fa-table"

    category = "Матрица компетенций"

    name = "Внешний ресурс"
    name_plural = "Внешние ресурсы"

    can_create = True
    can_edit = True
    can_view_details = True
    can_delete = True
    can_export = True

    form_args = {}
    form_include_pk = False
    form_columns = [
        ExternalResourceModel.name,
        ExternalResourceModel.url,
        ExternalResourceModel.context,
    ]
    form_overrides = {
        "context": ToastUIEditorField,
    }
    form_widget_args = {}
    form_ajax_refs = {}

    column_formatters = {
        ExternalResourceModel.context: lambda item, _: markdown_to_html(item.context),  # type: ignore[attr-defined]
    }
    column_formatters_detail = {
        ExternalResourceModel.context: lambda item, _: markdown_to_html(item.context),  # type: ignore[attr-defined]
    }
    column_labels = {
        ExternalResourceModel.name: "Название ресурса",
        ExternalResourceModel.url: "Ссылка на ресурс",
        ExternalResourceModel.context: "Контекст использования ресурса",
    }
    column_searchable_list = [ExternalResourceModel.name]
    column_default_sort = []
    column_sortable_list = []
    column_details_list = [
        ExternalResourceModel.id,
        ExternalResourceModel.name,
        ExternalResourceModel.url,
        ExternalResourceModel.context,
    ]
    column_list = [
        ExternalResourceModel.id,
        ExternalResourceModel.name,
    ]


class CompetencyMatrixItemView(
    ModelViewWithDeleteAction,
    ModelViewWithPublishAction,
    model=CompetencyMatrixItemModel,
):
    icon = "fa-solid fa-circle-question"
    category_icon = "fa-solid fa-table"

    category = "Матрица компетенций"

    name = "Вопрос"
    name_plural = "Вопросы"

    can_create = True
    can_edit = True
    can_view_details = True
    can_delete = True
    can_export = True

    form_args = {}
    form_include_pk = False
    form_columns = [
        CompetencyMatrixItemModel.sheet,
        CompetencyMatrixItemModel.section,
        CompetencyMatrixItemModel.subsection,
        CompetencyMatrixItemModel.grade,
        CompetencyMatrixItemModel.question,
        CompetencyMatrixItemModel.answer,
        CompetencyMatrixItemModel.interview_expected_answer,
        CompetencyMatrixItemModel.resources,
    ]
    form_overrides = {
        "answer": ToastUIEditorField,
        "interview_expected_answer": ToastUIEditorField,
    }
    form_widget_args = {
        "published_at": {
            "readonly": True,
        },
    }
    form_ajax_refs = {
        "resources": {
            "fields": ("id", "name", "url", "context"),
            "order_by": "name",
        },
    }

    column_formatters = {
        CompetencyMatrixItemModel.grade: lambda item, _: item.grade.value,  # type: ignore[attr-defined]
        CompetencyMatrixItemModel.publish_status: lambda item, _: item.publish_status.label,  # type: ignore[attr-defined]
        CompetencyMatrixItemModel.published_at: lambda item, _: item.published_at.strftime(  # type: ignore[attr-defined]
            "%m/%d/%Y %I:%M:%S %p (UTC)",
        ),
        CompetencyMatrixItemModel.answer: lambda item, _: markdown_to_html(item.answer),  # type: ignore[attr-defined]
        CompetencyMatrixItemModel.interview_expected_answer: lambda item, _: markdown_to_html(
            item.interview_expected_answer,  # type: ignore[attr-defined]
        ),
    }
    column_formatters_detail = {
        CompetencyMatrixItemModel.grade: lambda item, _: item.grade.value,  # type: ignore[attr-defined]
        CompetencyMatrixItemModel.publish_status: lambda item, _: item.publish_status.label,  # type: ignore[attr-defined]
        CompetencyMatrixItemModel.published_at: lambda item, _: item.published_at.strftime(  # type: ignore[attr-defined]
            "%m/%d/%Y %I:%M:%S %p (UTC)",
        ),
        CompetencyMatrixItemModel.answer: lambda item, _: markdown_to_html(item.answer),  # type: ignore[attr-defined]
        CompetencyMatrixItemModel.interview_expected_answer: lambda item, _: markdown_to_html(
            item.interview_expected_answer,  # type: ignore[attr-defined]
        ),
    }
    column_labels = {
        CompetencyMatrixItemModel.id: "Идентификатор",
        CompetencyMatrixItemModel.sheet: "Лист",
        CompetencyMatrixItemModel.section: "Раздел",
        CompetencyMatrixItemModel.subsection: "Подраздел",
        CompetencyMatrixItemModel.grade: "Грейд",
        CompetencyMatrixItemModel.question: "Вопрос",
        CompetencyMatrixItemModel.answer: "Ответ",
        CompetencyMatrixItemModel.interview_expected_answer: "Ожидаемый ответ на собеседовании",
        CompetencyMatrixItemModel.resources: "Внешние ресурсы",
        CompetencyMatrixItemModel.publish_status: "Статус",
        CompetencyMatrixItemModel.published_at: "Время публикации",
    }
    column_searchable_list = [
        CompetencyMatrixItemModel.question,
        CompetencyMatrixItemModel.sheet,
        CompetencyMatrixItemModel.section,
        CompetencyMatrixItemModel.subsection,
        CompetencyMatrixItemModel.grade,
    ]
    column_default_sort = [
        (CompetencyMatrixItemModel.sheet, True),
        (CompetencyMatrixItemModel.section, True),
        (CompetencyMatrixItemModel.subsection, True),
        (CompetencyMatrixItemModel.grade, True),
        (CompetencyMatrixItemModel.question, True),
    ]
    column_sortable_list = [
        CompetencyMatrixItemModel.id,
        CompetencyMatrixItemModel.question,
        CompetencyMatrixItemModel.sheet,
        CompetencyMatrixItemModel.section,
        CompetencyMatrixItemModel.subsection,
        CompetencyMatrixItemModel.grade,
        CompetencyMatrixItemModel.publish_status,
    ]
    column_details_list = [
        CompetencyMatrixItemModel.id,
        CompetencyMatrixItemModel.sheet,
        CompetencyMatrixItemModel.section,
        CompetencyMatrixItemModel.subsection,
        CompetencyMatrixItemModel.grade,
        CompetencyMatrixItemModel.question,
        CompetencyMatrixItemModel.answer,
        CompetencyMatrixItemModel.interview_expected_answer,
        CompetencyMatrixItemModel.publish_status,
        CompetencyMatrixItemModel.published_at,
        CompetencyMatrixItemModel.resources,
    ]
    column_list = [
        CompetencyMatrixItemModel.id,
        CompetencyMatrixItemModel.question,
        CompetencyMatrixItemModel.sheet,
        CompetencyMatrixItemModel.section,
        CompetencyMatrixItemModel.subsection,
        CompetencyMatrixItemModel.grade,
        CompetencyMatrixItemModel.publish_status,
    ]
