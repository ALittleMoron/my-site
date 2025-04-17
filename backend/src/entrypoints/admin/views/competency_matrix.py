from wtforms.fields.simple import TextAreaField

from db.models import CompetencyMatrixItemModel, ExternalResourceModel
from entrypoints.admin.views.base import ModelViewWithAction


class ExternalResourceView(ModelViewWithAction, model=ExternalResourceModel):
    icon = "fa-solid fa-book-open"

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
        "context": TextAreaField,
    }
    form_widget_args = {}
    form_ajax_refs = {}

    column_formatters = {}
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


class CompetencyMatrixItemView(ModelViewWithAction, model=CompetencyMatrixItemModel):
    icon = "fa-solid fa-table"

    name_plural = "Матрица компетенций"

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
        CompetencyMatrixItemModel.status,
        CompetencyMatrixItemModel.resources,
    ]
    form_overrides = {
        "answer": TextAreaField,
        "interview_expected_answer": TextAreaField,
    }
    form_widget_args = {}
    form_ajax_refs = {
        "resources": {
            "fields": ("id", "name", "url", "context"),
            "order_by": "name",
        }
    }

    column_formatters = {}
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
        CompetencyMatrixItemModel.status,
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
        CompetencyMatrixItemModel.status,
        CompetencyMatrixItemModel.resources,
    ]
    column_list = [
        CompetencyMatrixItemModel.id,
        CompetencyMatrixItemModel.question,
        CompetencyMatrixItemModel.sheet,
        CompetencyMatrixItemModel.section,
        CompetencyMatrixItemModel.subsection,
        CompetencyMatrixItemModel.grade,
        CompetencyMatrixItemModel.status,
    ]
