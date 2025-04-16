from db.models import CompetencyMatrixItemModel
from entrypoints.admin.views.base import ModelViewWithAction


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
    form_columns = []
    form_overrides = {}
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
    column_searchable_list = []
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
